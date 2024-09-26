from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phoneNumber = models.CharField(max_length=12)
    responseCode = models.CharField(max_length=50, blank = True)
    responseDescription = models.CharField(max_length=50, blank = True)
    merchantRequestID = models.CharField(max_length=200, blank = True)
    transactionId = models.CharField(max_length=50, blank = True)
    createdAt = models.DateTimeField(auto_now_add=True, auto_now = False, blank = True)
    updatedAt = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return (
            f"Payment(id={self.id}, amount={self.amount}, "
            f"phoneNumber='{self.phoneNumber}', transactionType='{self.responseCode}', "
            f"responseDescription='{self.responseDescription}', merchantRequestID='{self.merchantRequestID}', "
            f"transactionId='{self.transactionId}', createdAt={self.createdAt}, "
            f"updatedAt={self.updatedAt}, user={self.user})"
        )

# id Int @default(autoincrement()) @id
#   amount Int
#   phoneNumber String
#   transactionType String?
#   businessShortCode String?
#   callbackUrl String?
#   transactionId String?
#   createdAt DateTime @default(now())
#   updatedAt DateTime @updatedAt