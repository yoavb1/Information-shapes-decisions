from django.db import models

class Participant(models.Model):

    user_id = models.CharField(max_length=4)
    condition = models.CharField(max_length=2)
    date = models.CharField(max_length=50)
    ip = models.CharField(max_length=50)
    aid = models.CharField(max_length=50)

    class Meta:
        # Gives the proper plural name for admin
        verbose_name_plural = "Participants"

    def __str__(self):
        return self.user_id

class PaymentCode(models.Model):

    user_id = models.CharField(max_length=4)
    time = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    condition = models.CharField(max_length=2)
    payment_code = models.CharField(max_length=20)

    class Meta:
        # Gives the proper plural name for admin
        verbose_name_plural = "PaymentCode"

    def __str__(self):
        return '{} - {}'.format(self.user_id, self.name)

class Classification(models.Model):

    user_id = models.CharField(max_length=5)
    block = models.CharField(max_length=1)
    trial = models.CharField(max_length=3)
    event_type = models.CharField(max_length=8)
    stimulus = models.CharField(max_length=100)
    alarm_output = models.CharField(max_length=2)
    user_action = models.CharField(max_length=5)
    score = models.CharField(max_length=4)
    alert_system = models.CharField(max_length=5, default='-')
    condition = models.CharField(max_length=5, default='-')
    classification_time = models.CharField(max_length=100, default='-')
    event_time = models.CharField(max_length=100, default='-')


    class Meta:
        # Gives the proper plural name for admin
        verbose_name_plural = "Classifications"

    def __str__(self):
        return 'user: {}, block: {}, trial: {}'.format(self.user_id, self.block, self.trial)

class Block(models.Model):

    user_id = models.CharField(max_length=4)
    block = models.CharField(max_length=50)
    score = models.CharField(max_length=50)
    alert_system = models.CharField(max_length=50)
    condition = models.CharField(max_length=2)


    class Meta:
        # Gives the proper plural name for admin
        verbose_name_plural = "Blocks"

    def __str__(self):
        return '{} - block: {}, score: {}, alert system: {}'.\
                format(self.user_id, self.block, self.block, self.alert_system)



