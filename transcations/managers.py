from django.db import models


class TranscationsQueryset(models.QuerySet):

    def is_active(self):
        return self.filter(active=True)

    def filter_by_date(self, date_start, date_end):
        return self.filter(date_expired__range=[date_start, date_end])


class GeneralManager(models.Manager):

    def get_queryset(self):
         return TranscationsQueryset(self.model, using=self._db,)

    def not_paid(self):
        return self.get_queryset().filter(is_paid=False)


class BillCategoryManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)


class PersonManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)


class ExpenseCategoryManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)


class OccupationManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)