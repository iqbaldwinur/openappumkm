from django.db import models
from django.db.models import Sum, F, DecimalField
from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, username, email, fullname, nomortelephone, role, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            fullname=fullname,
            nomortelephone=nomortelephone,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, fullname, nomortelephone, role, password=None):
        user = self.create_user(
            username,
            email,
            fullname,
            nomortelephone,
            role,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class MasterUser(AbstractBaseUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    fullname = models.CharField(max_length=255)
    nomortelephone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'fullname', 'nomortelephone', 'role']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class MasterBelanja(models.Model):
    nama = models.CharField(max_length=200)
   
    
    def __str__(self):
        return self.nama


class MasterPendapatan(models.Model):
    nama = models.CharField(max_length=200)
    tgl_pendapatan = models.DateField()
    kode_pendapatan = models.CharField(max_length=100)
    urai_pendapatan = models.TextField()
    status = models.CharField(max_length=100)
    nilai_uang = models.DecimalField(max_digits=12, decimal_places=2)
    bulan = models.IntegerField()
    bukti = models.FileField(upload_to='bukti/')
    keterangan = models.TextField()
    user = models.ForeignKey(MasterUser, on_delete=models.CASCADE)

class RencanaAnggaranBelanja(models.Model):
    nama_keperluan = models.CharField(max_length=200)
    tgl_mulai = models.DateField()
    tgl_berakhir = models.DateField()
    user = models.ForeignKey(MasterUser, on_delete=models.CASCADE)
    deskripsi = models.TextField()

class Anggaran(models.Model):
    belanja = models.ForeignKey(MasterBelanja, on_delete=models.CASCADE)
    anggaran = models.DecimalField(max_digits=12, decimal_places=2)
    user = models.ForeignKey(MasterUser, on_delete=models.CASCADE)
    rencana_anggaran_belanja = models.ForeignKey(RencanaAnggaranBelanja, on_delete=models.CASCADE)



class DistribusiModal(models.Model):
    TANGGAL_STATUS_CHOICES = (
        ('transfer', 'Transfer'),
        ('cash', 'Cash'),
    )

    REKENING_CHOICES = (
        ('utama', 'Rekening Utama'),
        ('lainnya', 'Rekening Lainnya'),
    )

    
    tanggal_masuk = models.DateField()
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    sumber = models.CharField(max_length=50, choices=REKENING_CHOICES)
    status = models.CharField(max_length=50, choices=TANGGAL_STATUS_CHOICES)
    keperluan_bulan = models.CharField(max_length=50)

    def __str__(self):
        return {self.tanggal_masuk}


class SSH(models.Model):
    URAIAN_CHOICES = [
        ('bulan', 'Bulan'),
        ('box', 'Box'),
        ('paket', 'Paket'),
        ('buah', 'Buah'),
        ('kali', 'Kali'),
        # tambahkan pilihan lain jika diperlukan
    ]

    uraian = models.TextField()
    satuan = models.CharField(max_length=20, choices=URAIAN_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uraian} - {self.get_satuan_display()}"
    
class TransaksiAnggaranBelanja(models.Model):
    tgl_anggaran = models.DateField()
    store = models.CharField(max_length=255)
    keterangan = models.TextField()
    jumlah_anggaran = models.DecimalField(max_digits=12, decimal_places=2)
    def getmonth(self):
        if self.tgl_anggaran.month == 1 : 
            return 'januari'
        elif self.tgl_anggaran.month == 2 : 
            return 'februari'
        elif self.tgl_anggaran.month == 3 :
            return 'maret'
        elif self.tgl_anggaran.month == 4 : 
            return 'april'
        elif self.tgl_anggaran.month == 5 : 
            return 'mei'
        elif self.tgl_anggaran.month == 6 : 
            return 'juni'
        elif self.tgl_anggaran.month == 7 : 
            return 'juli'
        elif self.tgl_anggaran.month == 8 : 
            return 'agustus'
        elif self.tgl_anggaran.month == 9 : 
            return 'september'
        elif self.tgl_anggaran.month == 10 : 
            return 'oktober'
        elif self.tgl_anggaran.month == 11 : 
            return 'november'
        elif self.tgl_anggaran.month == 12 : 
            return 'desember'
    
    def __str__(self):
        return f"{self.tgl_anggaran} - {self.store}"
    
    
    def update_realisasi(self):
        total_realisasi = self.barang_set.aggregate(total=Sum(F('jumlah') * F('harga'), output_field=DecimalField()))['total'] or Decimal('0.00')
        self.realisasi = total_realisasi
        self.save()
class TransaksiBelanja(models.Model):
    # anggaran = models.ForeignKey(Anggaran, on_delete=models.CASCADE, related_name='transaksi_belanja')
    kode_belanja = models.ForeignKey(MasterBelanja, on_delete=models.CASCADE)
    tgl_belanja = models.DateField()
    store = models.CharField(max_length=100)
    upload_bukti = models.FileField(upload_to='bukti/')
    keterangan = models.TextField()
    kode_transaksi_belanja = models.ForeignKey(TransaksiAnggaranBelanja, on_delete=models.CASCADE, related_name='transaksi_realisasi')
    urai_belanja = models.TextField()
    jumlah = models.IntegerField()
    realisasi = models.DecimalField(max_digits=10, decimal_places=2)
    sisa = models.DecimalField(max_digits=10, decimal_places=2)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)

   
    def __str__(self):
        return f"{self.kode_belanja.nama} - {self.tgl_belanja}"  
    
    
class Barang(models.Model):
    
    kode_belanja = models.ForeignKey(MasterBelanja, on_delete=models.CASCADE)
    transaksi_anggaran = models.ForeignKey(TransaksiAnggaranBelanja, on_delete=models.CASCADE, related_name='barang_set')
    jumlah = models.IntegerField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.transaksi_anggaran.update_realisasi()
    
    
    
class Transaksi(models.Model):
    tanggal = models.DateField()
    store = models.CharField(max_length=255)
    keterangan = models.TextField()
    jumlah_anggaran = models.ForeignKey(TransaksiAnggaranBelanja, on_delete=models.CASCADE)
    jumlah_realisasi = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selisih = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def update_realisasi(self):
        total_realisasi = sum(barang.harga for barang in self.jumlah_anggaran.barang_set.all())
        self.jumlah_realisasi = total_realisasi
        self.selisih = self.jumlah_anggaran.jumlah_anggaran - total_realisasi
        self.save()
    
