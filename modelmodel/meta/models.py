from django.db import models


class MakeModel(models.Model):
    name = models.CharField(
        verbose_name='Model Name', max_length=50, unique=True)

    def __str__(self):
        return self.name


FIELD_TYPE_CHOICES = (
    (name, name) for name in ['TextField', 'IntegerField']
)


class MakeField(models.Model):
    name = models.CharField(max_length=50)
    make_model = models.ForeignKey(MakeModel, on_delete=models.CASCADE)
    field_type = models.CharField(max_length=255, choices=FIELD_TYPE_CHOICES)

    def __str__(self):
        return self.name


class MakeMigration(models.Model):
    name = models.CharField(verbose_name='Migration Name', max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.name
