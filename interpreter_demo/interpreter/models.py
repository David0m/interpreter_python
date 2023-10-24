from django.db import models


class CodeSnippet(models.Model):
    code = models.TextField()
    iputdata = models.CharField(max_length=255)
    outputdata = models.CharField(max_length=255)
    result = models.TextField()

    class Meta:
        verbose_name = 'интерпретатор'
        verbose_name_plural = 'не подлежит редактированию'


class TestCode(models.Model):
    title = models.CharField(max_length=256, verbose_name='Название')
    TaskDescription = models.TextField(verbose_name='Описание задания')
    task_variables = models.CharField(max_length=256,
                                      verbose_name='Переменные'
                                      )

    class Meta:
        verbose_name = 'Задачу'
        verbose_name_plural = 'Список задач'

    def __str__(self):
        return self.title


class TestData(models.Model):
    vvod = models.TextField(verbose_name='Вводные данные')
    RightRes = models.TextField(verbose_name='Правильный ответ')
    test_code = models.ForeignKey(TestCode, on_delete=models.CASCADE,
                                  related_name='testdata',
                                  verbose_name='Связь с задачей'
                                  )
    outputdata = models.TextField(null=True, blank=True,
                                  verbose_name='Выходные данные'
                                  )
    Result = models.BooleanField(null=True, blank=True,
                                 verbose_name='Результат'
                                 )

    class Meta:
        verbose_name = 'Тестовые данные'
        verbose_name_plural = 'Тестовые данные'

    def __str__(self):
        return str(self.test_code.title + " - тестовые данные")


class UserCode(models.Model):
    code = models.TextField()
    iputdata = models.CharField(max_length=255)
    outputdata = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Пользовательский код'
        verbose_name_plural = 'Пользовательские коды'

    def __str__(self):
        return str("Код пользователя")
