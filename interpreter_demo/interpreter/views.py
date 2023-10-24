from django.shortcuts import render, redirect
from .models import CodeSnippet
from django.http import JsonResponse
import io
import contextlib
import traceback
from interpreter.models import TestCode, TestData, UserCode
import ast
import astor


def task_list(request):
    tasks = TestCode.objects.all()
    return render(request, 'interpreter/task_list.html', {'tasks': tasks})


class ReplaceAssign(ast.NodeTransformer):
    def __init__(self, task_variables, input_data):
        self.task_variables = task_variables
        self.input_data = input_data

    def visit_Assign(self, node):
        if isinstance(
            node.targets[0], ast.Name
        ) and node.targets[0].id in self.task_variables:

            index = self.task_variables.index(node.targets[0].id)
            input_data = self.input_data[index].strip()
            if input_data.isdigit():
                value = ast.Num(int(input_data))
            else:
                value = ast.Str(input_data)
            return ast.Assign(targets=node.targets, value=value)
        return node


def replace_code_variables(code, task_variables, input_data):
    tree = ast.parse(code)
    new_tree = ReplaceAssign(task_variables, input_data).visit(tree)
    return astor.to_source(new_tree)


def run_test(request):
    if request.method == 'POST' and request.headers.get(
        'X-Requested-With'
    ) == 'XMLHttpRequest':

        input_data = request.POST.get('vvod').split(",")
        code = CodeSnippet.objects.last().code
        testdata = TestData.objects.get(vvod=','.join(input_data))
        test_code = testdata.test_code
        task_variables = test_code.task_variables.split(", ")
        code_with_data = replace_code_variables(code,
                                                task_variables,
                                                input_data
                                                )
        output_data, _, error_message = interpret_code(code_with_data)
        testdata.outputdata = output_data if not error_message else str(
            error_message
            )
        testdata.save()
        expected_result = testdata.RightRes
        result = output_data == expected_result if not error_message else False

        return JsonResponse({'outputdata': testdata.outputdata,
                            'Result': result,
                             'error_message': str(error_message)
                             if error_message else None
                             }
                            )


def interpret_code(code):
    try:
        global_vars = {}
        local_vars = {}
        with contextlib.redirect_stdout(io.StringIO()) as f:
            exec(code, global_vars, local_vars)

        filtered_local_vars = {k: v for k, v in local_vars.items()
                               if not k.startswith("__")
                               }

        return f.getvalue().strip(), filtered_local_vars, ""
    except Exception:
        tb = traceback.format_exc().split('\n')
        last_line = tb[-3], tb[-2] if len(tb) > 1 else ""
        return "", {}, last_line


def interpreter(request, task_id=None):
    if task_id:
        testcode = TestCode.objects.get(id=task_id)
        task_description = testcode.TaskDescription
    else:
        task_description = ''

    if request.method == 'POST':
        code = request.POST['code']
        output, local_vars, error_message = interpret_code(code)
        snippet = CodeSnippet(code=code,
                              outputdata=output
                              )
        snippet.save()

        local_vars_string = ", ".join(f"{k} = {v}" for k, v in
                                      local_vars.items()
                                      )

        return JsonResponse({'local_vars': local_vars_string,
                             'code_result': output,
                             'error_message': error_message
                             }
                            )

    tasks = TestCode.objects.all()
    testdata = testdata = TestData.objects.filter(test_code=task_id)
    return render(request, 'interpreter/interpreter.html',
                  {
                      'tasks': tasks,
                      'testdata': testdata,
                      'task_description': task_description
                   }
                  )


def save_code(request):
    code = request.POST.get('code')
    iputdata = request.POST.get('iputdata')
    outputdata = request.POST.get('outputdata')

    user_code = UserCode(code=code, iputdata=iputdata, outputdata=outputdata)
    user_code.save()

    return redirect('index:send_success')


def send_success(request):
    return render(request, 'interpreter/send_success.html')
