from django.db import models
from django.utils import timezone

class Patient(models.Model):
    name = models.CharField(max_length=100, verbose_name="রোগীর নাম")
    phone = models.CharField(max_length=15, blank=True, verbose_name="ফোন নম্বর")
    address = models.TextField(blank=True, verbose_name="ঠিকানা")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="তৈরির তারিখ")
    
    class Meta:
        verbose_name = "রোগী"
        verbose_name_plural = "রোগীরা"
    
    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=200, verbose_name="ওষুধের নাম")
    company = models.CharField(max_length=100, blank=True, verbose_name="কোম্পানি")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="একক দাম")
    stock_quantity = models.IntegerField(default=0, verbose_name="স্টক পরিমাণ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="তৈরির তারিখ")
    
    class Meta:
        verbose_name = "ওষুধ"
        verbose_name_plural = "ওষুধসমূহ"
    
    def __str__(self):
        return f"{self.name} - {self.company}"

class Purchase(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, verbose_name="ওষুধ")
    quantity = models.IntegerField(verbose_name="পরিমাণ")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="একক খরচ")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="মোট খরচ")
    purchase_date = models.DateTimeField(default=timezone.now, verbose_name="কেনার তারিখ")
    supplier = models.CharField(max_length=100, blank=True, verbose_name="সরবরাহকারী")
    
    class Meta:
        verbose_name = "ক্রয়"
        verbose_name_plural = "ক্রয়সমূহ"
    
    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
        # স্টক আপডেট
        self.medicine.stock_quantity += self.quantity
        self.medicine.save()
    
    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} পিস"

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="রোগী")
    visit_date = models.DateTimeField(default=timezone.now, verbose_name="ভিজিটের তারিখ")
    prescription = models.TextField(blank=True, verbose_name="প্রেসক্রিপশন")
    
    class Meta:
        verbose_name = "ভিজিট"
        verbose_name_plural = "ভিজিটসমূহ"
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.patient.name} - {self.visit_date.strftime('%d/%m/%Y')}"

class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'নগদ'),
        ('credit', 'বাকি'),
    ]
    
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, verbose_name="ভিজিট")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, verbose_name="ওষুধ")
    quantity = models.IntegerField(verbose_name="পরিমাণ")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="একক দাম")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="মোট দাম")
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash', verbose_name="পেমেন্ট ধরন")
    sale_date = models.DateTimeField(default=timezone.now, verbose_name="বিক্রয়ের তারিখ")
    
    class Meta:
        verbose_name = "বিক্রয়"
        verbose_name_plural = "বিক্রয়সমূহ"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # স্টক কমানো
        if self.medicine.stock_quantity >= self.quantity:
            self.medicine.stock_quantity -= self.quantity
            self.medicine.save()
    
    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} পিস - {self.get_payment_type_display()}"