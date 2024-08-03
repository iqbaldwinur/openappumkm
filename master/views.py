from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import MasterPendapatan, Anggaran, MasterUser, MasterBelanja, DistribusiModal, SSH, TransaksiAnggaranBelanja, TransaksiBelanja, Barang, Transaksi
from .forms import TransaksiBelanja, AnggaranForm, CustomUserChangeForm, CustomUserCreationForm, MasterBelanja
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from django.contrib.auth import login
from .decorators import role_required
from django.db import transaction, IntegrityError
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.loader import get_template
from xhtml2pdf import pisa








def index(request):
    return render(request, 'master/index.html')

@login_required
@role_required(allowed_roles=['admin'])
def dashboard_view(request):
    pendapatan = MasterPendapatan.objects.all()
    transaksi = TransaksiBelanja.objects.all()
    transaksi_terbaru = TransaksiBelanja.objects.order_by('-tgl_belanja')[:5]
    context = {
        pendapatan : pendapatan,
        transaksi : transaksi,
        transaksi_terbaru : transaksi_terbaru
    }

    return render(request, 'master/dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def transaksi_belanja_list(request, transaksi_id=None):
    transaksi_belanja = TransaksiBelanja.objects.filter(kode_transaksi_belanja=transaksi_id) if transaksi_id else TransaksiBelanja.objects.all()
    belanja = MasterBelanja.objects.all()
    transaksi_anggaran_belanja = TransaksiAnggaranBelanja.objects.all()
    
    return render(request, 'master/transaksi_belanja_list.html', {
        'transaksi_belanja': transaksi_belanja,
        'belanja': belanja,
        'transaksi_anggaran_belanja': transaksi_anggaran_belanja,
        'transaksi_id': transaksi_id
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_transaksi_belanja(request, transaksi_id):
    if request.method == 'POST':
        try:
            kode_belanja_id = request.POST.get('kode_belanja')
            tgl_belanja = request.POST.get('tgl_belanja')
            store = request.POST.get('store')
            upload_bukti = request.FILES.get('upload_bukti')
            keterangan = request.POST.get('keterangan')
            kode_transaksi_belanja_id = request.POST.get('kode_transaksi_belanja')
            urai_belanja = request.POST.get('urai_belanja')
            jumlah = request.POST.get('jumlah')
            realisasi = request.POST.get('realisasi')
            
           

            # Mengambil objek dari database berdasarkan ID yang diberikan
            kode_belanja = get_object_or_404(MasterBelanja, id=kode_belanja_id)
            kode_transaksi_belanja = get_object_or_404(TransaksiAnggaranBelanja, id=kode_transaksi_belanja_id)

            # Konversi jumlah dan realisasi menjadi Decimal
            jumlah = Decimal(jumlah)
            realisasi = Decimal(realisasi)

            # Menghitung sisa anggaran yang tersedia
            sisa = kode_transaksi_belanja.jumlah_anggaran - realisasi

            # Menghitung saldo distribusi modal berdasarkan bulan anggaran
            saldo_aggregate = DistribusiModal.objects.filter(keperluan_bulan=kode_transaksi_belanja.getmonth()).aggregate(total_nominal=Sum('nominal', default=0))
            total_nominal = saldo_aggregate['total_nominal'] if saldo_aggregate['total_nominal'] is not None else Decimal('0.00')
            saldo = total_nominal - realisasi

            # Memeriksa apakah realisasi melebihi saldo yang tersedia
            if realisasi > saldo:
                messages.error(request, 'Realisasi melebihi saldo distribusi modal.')
                return redirect('transaksi_belanja_list')

            # Membuat objek TransaksiBelanja baru
            TransaksiBelanja.objects.create(
                kode_belanja=kode_belanja,
                tgl_belanja=tgl_belanja,
                store=store,
                upload_bukti=upload_bukti,
                keterangan=keterangan,
                kode_transaksi_belanja=kode_transaksi_belanja,
                urai_belanja=urai_belanja,
                jumlah=jumlah,
                realisasi=realisasi,
                sisa=sisa,
                saldo=saldo
            )
            # Redirect ke halaman daftar transaksi belanja setelah transaksi berhasil dibuat
            return redirect('transaksi_belanja_list', transaksi_id=transaksi_id)

        except Exception as e:
            # Tangani semua pengecualian yang tidak terduga
            messages.error(request, f'Terjadi kesalahan: {e}')
            return redirect('transaksi_belanja_list', transaksi_id=transaksi_id)

    # Jika request method bukan POST, render halaman daftar transaksi belanja
    return render(request, 'master/transaksi_belanja_list.html', {
        'transaksi_id': transaksi_id
    })
    # master_belanja_list = MasterBelanja.objects.all()
    # return render(request, 'create_transaksi_realisasi.html', {'master_belanja_list': master_belanja_list})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_transaksi_belanja(request, transaksi_id, belanja_id):
    transaksi_belanja = get_object_or_404(TransaksiBelanja, kode_transaksi_belanja=transaksi_id, id=belanja_id)
    print(transaksi_belanja)
    if request.method == 'POST':
        try:
            kode_belanja = request.POST.get('kode_belanja')
            tgl_belanja = request.POST.get('tgl_belanja')
            store = request.POST.get('store')
            upload_bukti = request.FILES.get('upload_bukti')
            keterangan = request.POST.get('keterangan')
            urai_belanja = request.POST.get('urai_belanja')
            jumlah = request.POST.get('jumlah')
            realisasi = request.POST.get('realisasi')

            if kode_belanja:
                transaksi_belanja.kode_belanja = MasterBelanja.objects.get(id=kode_belanja)
            transaksi_belanja.tgl_belanja = tgl_belanja
            transaksi_belanja.store = store
            if upload_bukti:
                transaksi_belanja.upload_bukti = upload_bukti
            transaksi_belanja.keterangan = keterangan
            transaksi_belanja.urai_belanja = urai_belanja
            transaksi_belanja.jumlah = jumlah
            transaksi_belanja.realisasi = realisasi

            transaksi_anggaran_belanja = TransaksiAnggaranBelanja.objects.get(id=transaksi_id)
            sisa = transaksi_anggaran_belanja.jumlah_anggaran - Decimal(realisasi)

            saldo_aggregate = DistribusiModal.objects.filter(keperluan_bulan=transaksi_anggaran_belanja.getmonth()).aggregate(total_nominal=Sum('nominal', default=0))
            total_nominal = saldo_aggregate['total_nominal'] if saldo_aggregate['total_nominal'] is not None else Decimal('0.00')
            saldo = total_nominal - Decimal(realisasi)

            if Decimal(realisasi) > saldo:
                messages.error(request, 'Realisasi melebihi saldo distribusi modal.')
                return redirect('transaksi_belanja_list', transaksi_id=transaksi_id)

            transaksi_belanja.sisa = sisa
            transaksi_belanja.saldo = saldo

            transaksi_belanja.save()

            messages.success(request, 'Transaksi belanja berhasil diubah.')
            return redirect('transaksi_belanja_list', transaksi_id=transaksi_id)

        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {e}')
            return redirect('transaksi_belanja_list', transaksi_id=transaksi_id)

    return JsonResponse({
        'html': render_to_string('master/edit_transaksi_modal.html', {'transaksi_belanja': transaksi_belanja}),
    })



@login_required
@user_passes_test(lambda u: u.is_superuser)
def transaksi_belanja_list(request, transaksi_id=None):
    transaksi_belanja = TransaksiBelanja.objects.filter(kode_transaksi_belanja=transaksi_id) if transaksi_id else TransaksiBelanja.objects.all()
    belanja = MasterBelanja.objects.all()
    transaksi_anggaran_belanja = TransaksiAnggaranBelanja.objects.all()
    
    return render(request, 'master/transaksi_belanja_list.html', {
        'transaksi_belanja': transaksi_belanja,
        'belanja': belanja,
        'transaksi_anggaran_belanja': transaksi_anggaran_belanja,
        'transaksi_id': transaksi_id
    })
    
@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_transaksi_belanja(request, transaksi_id, belanja_id):
    print(f"Deleting Transaksi Belanja: transaksi_id={transaksi_id}, belanja_id={belanja_id}")
    transaksi_belanja = get_object_or_404(TransaksiBelanja, id=belanja_id)
    transaksi_belanja.delete()
    return redirect('transaksi_belanja_list', transaksi_id=transaksi_id)



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(
        html, dest=response
    )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
        
@login_required
@user_passes_test(lambda u: u.is_superuser)
def transaksi_belanja_pdf(request, transaksi_id=None):
    transaksi_belanja = TransaksiBelanja.objects.filter(kode_transaksi_belanja=transaksi_id) if transaksi_id else TransaksiBelanja.objects.all()
    belanja = MasterBelanja.objects.all()
    transaksi_anggaran_belanja = TransaksiAnggaranBelanja.objects.all()
    
    context = {
        'transaksi_belanja': transaksi_belanja,
        'belanja': belanja,
        'transaksi_anggaran_belanja': transaksi_anggaran_belanja,
        'transaksi_id': transaksi_id
    }

    pdf = render_to_pdf('master/transaksi_belanja_pdf.html', context)
    return HttpResponse(pdf, content_type='application/pdf')

# anggaran
def anggaran_list(request):
    anggarans = Anggaran.objects.all()
    return render(request, 'master/anggaran_list.html', {'anggarans': anggarans})



def anggaran_create(request):
    if request.method == 'POST':
        form = AnggaranForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('anggaran_list')
    else:
        form = AnggaranForm()
    return render(request, 'master/anggaran_form.html', {'form': form})


def anggaran_update(request, pk):
    anggaran = get_object_or_404(Anggaran, pk=pk)
    if request.method == 'POST':
        form = AnggaranForm(request.POST, instance=anggaran)
        if form.is_valid():
            form.save()
            return redirect('anggaran_list')
    else:
        form = AnggaranForm(instance=anggaran)
    return render(request, 'master/anggaran_form.html', {'form': form})

def anggaran_delete(request, pk):
    anggaran = get_object_or_404(Anggaran, pk=pk)
    if request.method == 'POST':
        anggaran.delete()
        return redirect('anggaran_list')
    return render(request, 'master/anggaran_confirm_delete.html', {'object': anggaran})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    users = MasterUser.objects.all()
    return render(request, 'master/manage_users.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'master/manage_users.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(MasterUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = CustomUserChangeForm(instance=user)
        
    users = MasterUser.objects.all()
    return render(request, 'master/manage_users.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
   user = get_object_or_404(MasterUser, id=user_id)
   user.delete()
   return redirect('manage_users')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def belanja_list(request):
    belanja = MasterBelanja.objects.all()
    print(belanja)
    return render(request, 'master/belanja_list.html', {'belanja': belanja})


def create_belanja(request):
    if request.method == 'POST':
        belanja = MasterBelanja()
        nama = request.POST.get('nama')
        
        try:
            with transaction.atomic():
                belanja.nama = nama
                belanja.save()
                return redirect('belanja_list')
        except IntegrityError:
            print('error')
            return redirect('belanja_list')
        
        
@login_required
@user_passes_test(lambda u: u.is_superuser)
def belanja_delete(request, user_id):
    belanja = get_object_or_404(MasterBelanja, id=user_id)
    belanja.delete()
    return redirect('belanja_list')
    
@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_belanja(request, belanja_id):
    if request.method == 'POST':
        belanja = get_object_or_404(MasterBelanja, id=belanja_id)
        
        nama = request.POST.get('nama')
        user = request.POST.get('user_id')
        keterangan = request.POST.get('keterangan')
        
        try:
            with transaction.atomic():
                belanja.nama = nama
                belanja.keterangan = keterangan
                belanja.user_id = user
                belanja.save()
                return redirect('belanja_list')
        except IntegrityError:
            print('error')
            
            
         
def distribusi_modal_list(request):
    distribusi_modal = DistribusiModal.objects.all()
    return render(request, 'master/distribusi_modal_list.html', {'distribusi_modal': distribusi_modal})

def create_distribusi_modal(request):
    if request.method == 'POST':
        tanggal_masuk = request.POST['tanggal_masuk']
        nominal = request.POST['nominal']
        sumber = request.POST['sumber']
        status = request.POST['status']
        keperluan_bulan = request.POST['keperluan_bulan']
       
        
        DistribusiModal.objects.create(
            tanggal_masuk=tanggal_masuk,
            nominal=nominal,
            sumber=sumber,
            status=status,
            keperluan_bulan=keperluan_bulan
        )
        
        return redirect('distribusi_modal_list')
          
            
            
def edit_distribusi_modal(request, distribusi_id):
    distribusi = get_object_or_404(DistribusiModal, id=distribusi_id)
    if request.method == 'POST':
        distribusi.tanggal_masuk = request.POST['tanggal_masuk']
        distribusi.nominal = request.POST['nominal']
        distribusi.sumber = request.POST['sumber']
        distribusi.status = request.POST['status']
        distribusi.keperluan_bulan = request.POST['keperluan_bulan']
        if request.FILES.get('bukti_transaksi'):
            distribusi.bukti_transaksi = request.FILES['bukti_transaksi']
        distribusi.save()
        return redirect('distribusi_modal_list')
        
def delete_distribusi_modal(request, distribusi_id):
    distribusi = get_object_or_404(DistribusiModal, id=distribusi_id)
    distribusi.delete()
    return redirect('distribusi_modal_list')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_transaksi_anggaran_belanja(request):
    if request.method == 'POST':
        tgl_anggaran = request.POST['tgl_anggaran']
        store = request.POST['store']
        keterangan = request.POST['keterangan']
        jumlah_anggaran = request.POST['jumlah_anggaran']

        TransaksiAnggaranBelanja.objects.create(
            tgl_anggaran=tgl_anggaran,
            store=store,
            keterangan=keterangan,
            jumlah_anggaran=jumlah_anggaran,
        )
        return redirect('transaksi_anggaran_belanja_list')

    return render(request, 'transaksi_anggaran_belanja_form.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def transaksi_anggaran_belanja_list(request):
    transaksi_anggaran_belanja = TransaksiAnggaranBelanja.objects.all()
    return render(request, 'master/transaksi_anggaran_belanja_list.html', {'transaksi_anggaran_belanja': transaksi_anggaran_belanja})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_transaksi_anggaran_belanja(request, id):
    transaksi_anggaran = get_object_or_404(TransaksiAnggaranBelanja, id=id)

    if request.method == 'POST':
        tgl_anggaran = request.POST['tgl_anggaran']
        store = request.POST['store']
        keterangan = request.POST['keterangan']
        jumlah_anggaran = request.POST['jumlah_anggaran']

        transaksi_anggaran.tgl_anggaran = tgl_anggaran
        transaksi_anggaran.store = store
        transaksi_anggaran.keterangan = keterangan
        transaksi_anggaran.jumlah_anggaran = jumlah_anggaran

        transaksi_anggaran.save()

        return redirect('transaksi_anggaran_belanja_list')

    return render(request, 'edit_anggaran_belanja.html', {'transaksi_anggaran': transaksi_anggaran})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_transaksi_anggaran_belanja(request, pk):
    transaksi_anggaran_belanja = get_object_or_404(TransaksiAnggaranBelanja, id=pk)
    transaksi_anggaran_belanja.delete()
    return redirect('transaksi_anggaran_belanja_list')



@login_required
@user_passes_test(lambda u: u.is_superuser)
def detail_anggaran_belanja_list(request, anggaran_id):
    transaksi_anggaran = Barang.objects.filter(transaksi_anggaran=anggaran_id)
    belanja = MasterBelanja.objects.all()
    transaksi_anggaran_belanja = TransaksiAnggaranBelanja.objects.all()

    return render(request, 'master/detail_anggaran_belanja_list.html', {'transaksi_anggaran': transaksi_anggaran, 'belanja': belanja, 'anggaran_id': anggaran_id, 'transaksi_anggaran_belanja': transaksi_anggaran_belanja})
        
@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_detail_transaksi_belanja(request, anggaran_id):
    transaksi_anggaran = get_object_or_404(TransaksiAnggaranBelanja, id=anggaran_id)
    
    if request.method == 'POST':
        kode_belanja_id = request.POST.get('kode_belanja')
        jumlah = request.POST.get('jumlah')
        harga = request.POST.get('harga')
        
        kode_belanja = get_object_or_404(MasterBelanja, id=kode_belanja_id)
        
        try:
            jumlah = int(jumlah)
            harga = Decimal(harga)
        except (ValueError, Decimal.InvalidOperation):
            return JsonResponse({'success': False, 'errors': 'Invalid data'})
        
        Barang.objects.create(
            kode_belanja=kode_belanja,
            transaksi_anggaran=transaksi_anggaran,
            jumlah=jumlah,
            harga=harga
        )
        return HttpResponseRedirect(reverse('detail_anggaran_belanja_list', args=[anggaran_id]))
    
    context = {
        'transaksi_anggaran': transaksi_anggaran,
        'belanja_list': MasterBelanja.objects.all()  # Assuming you want to display a list of MasterBelanja
    }
    return render(request, 'master/create_detail_transaksi_belanja.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_detail_transaksi_belanja(request, barang_id):
    barang = get_object_or_404(Barang, id=barang_id)
    anggaran_id = barang.transaksi_anggaran.id  # Mendapatkan anggaran_id untuk redirect
    
    if request.method == 'POST':
        kode_belanja_id = request.POST.get('kode_belanja')
        jumlah = request.POST.get('jumlah')
        harga = request.POST.get('harga')
        
        kode_belanja = get_object_or_404(MasterBelanja, id=kode_belanja_id)
        
        try:
            jumlah = int(jumlah)
            harga = Decimal(harga)
        except (ValueError, Decimal.InvalidOperation):
            return JsonResponse({'success': False, 'errors': 'Invalid data'})
        
        barang.kode_belanja = kode_belanja
        barang.jumlah = jumlah
        barang.harga = harga
        barang.save()
        return HttpResponseRedirect(reverse('detail_anggaran_belanja_list', args=[anggaran_id]))
    
    context = {
        'barang': barang,
    }
    return render(request, 'edit_detail_anggaran_belanja.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_detail_transaksi_belanja(request, barang_id):
    barang = get_object_or_404(Barang, id=barang_id)
    anggaran_id = barang.transaksi_anggaran.id  # Mendapatkan anggaran_id untuk redirect
    barang.delete()
    return HttpResponseRedirect(reverse('detail_anggaran_belanja_list', args=[anggaran_id]))


@login_required
def ssh_list(request):
    ssh = SSH.objects.all()
    return render(request, 'master/ssh_list.html', {'ssh': ssh})
            
@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_ssh(request):
    if request.method == 'POST':
        uraian = request.POST.get('uraian')
        satuan = request.POST.get('satuan')
        SSH.objects.create(uraian=uraian, satuan=satuan)
        return redirect('ssh_list')
    return redirect('ssh_list')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_ssh(request, ssh_id):
    ssh = get_object_or_404(SSH, id=ssh_id)
    if request.method == 'POST':
        ssh.uraian = request.POST.get('uraian')
        ssh.satuan = request.POST.get('satuan')
        ssh.save()
        return redirect('ssh_list')
    return redirect('ssh_list')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_ssh(request, ssh_id):
    ssh = get_object_or_404(SSH, id=ssh_id)
    ssh.delete()
    return redirect('ssh_list')

@login_required
def ssh_list(request):
    ssh = SSH.objects.all()
    return render(request, 'master/ssh_list.html', {'ssh': ssh})
        

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_transaksi(request):
    if request.method == 'POST':
        tanggal = request.POST.get('tanggal')
        store = request.POST.get('store')
        keterangan = request.POST.get('keterangan')
        jumlah_anggaran_id = request.POST.get('jumlah_anggaran')

        jumlah_anggaran = get_object_or_404(TransaksiAnggaranBelanja, id=jumlah_anggaran_id)

        transaksi = Transaksi.objects.create(
            tanggal=tanggal,
            store=store,
            keterangan=keterangan,
            jumlah_anggaran=jumlah_anggaran
        )

        # Hitung jumlah realisasi dan selisih
        transaksi.update_realisasi()

        return HttpResponseRedirect(reverse('transaksi_list'))

    anggaran_list = TransaksiAnggaranBelanja.objects.all()
    return render(request, 'master/transaksi_list.html', {'anggaran_list': anggaran_list})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def transaksi_list(request):
    transaksi_list = Transaksi.objects.all()
    anggaran_list = TransaksiAnggaranBelanja.objects.all()
    return render(request, 'master/transaksi_list.html', {'transaksi_list': transaksi_list, 'anggaran_list': anggaran_list})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_transaksi(request, id):
    transaksi = get_object_or_404(Transaksi, id=id)

    if request.method == 'POST':
        tanggal = request.POST['tanggal']
        store = request.POST['store']
        keterangan = request.POST['keterangan']
        jumlah_anggaran_id = request.POST['jumlah_anggaran']

        jumlah_anggaran = get_object_or_404(TransaksiAnggaranBelanja, id=jumlah_anggaran_id)

        transaksi.tanggal = tanggal
        transaksi.store = store
        transaksi.keterangan = keterangan
        transaksi.jumlah_anggaran = jumlah_anggaran

        transaksi.update_realisasi()

        return redirect('transaksi_list')

    anggaran_list = TransaksiAnggaranBelanja.objects.all()
    return render(request, 'edit_transaksi.html', {'transaksi': transaksi, 'anggaran_list': anggaran_list})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_transaksi(request, transaksi_id):
    transaksi = get_object_or_404(Transaksi, id=transaksi_id)
    transaksi.delete()
    return HttpResponseRedirect(reverse('transaksi_list'))  










# login
# class LoginView(View):
#     def get(self, request):
#         return render(request, 'accounts/login.html')
    
#     def post(self, request):
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = MasterUser(username=username)
        
#         if user:
#             if user.check_password(password):
#                 redirect('master/dashboard.html')
                
#             else:
#                 return HttpResponse('username atau password salah')

# def my_login_view(request):
#     if request.method == 'POST':
#         form = CustomLoginForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('master/dashboard.html')
#         else:
#             form = CustomLoginForm()
#             return render(request, 'master/login', {'form': form})



        

       

        


        








