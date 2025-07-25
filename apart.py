import os, time, json
from datetime import datetime, timedelta

os.system("clear")
print("=" * 10, "Tenant UI", "=" * 10)
print("Ketik perintah 'DATABASE' untuk melihat tenant account")

COMPLAINTS_FILE = 'laporan_tenant.json' # Nama file untuk menyimpan keluhan

def load_complaints():
    """Memuat keluhan dari json"""
    if not os.path.exists(COMPLAINTS_FILE):
        return [] # Kembalikan list kosong jika file gak exists
    try:
        with open(COMPLAINTS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError: # Tangani jika file JSON korup/kosong
        print(f"Peringatan!: File '{COMPLAINTS_FILE}' kosong atau korup. Memulai dengan data kosong")
        return []
    except Exception as e:
        print(f"Error saar memuat keluhan dari file: {e}")
        return []

def save_complaints(complaint_list):
    """Menyimpan keluhan ke file JSON"""
    with open(COMPLAINTS_FILE, 'w') as f:
        json.dump(complaint_list, f, indent=4) # indent=4 untuk format JSON yang rapi

#_=== Definisi Class ===_

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self, username, password):
        return self.username == username and self.password == password

# Identifikasi Tenant
class Tenant(User):
    def __init__(self, username, password, floor, unit_number, datetime):
        super().__init__(username, password)
        self.floor = floor
        self.unit_number = unit_number
        self.datetime = datetime
        print(f"Tenant '{self.username}', Lantai {self.floor}, Unit {self.unit_number}" )


    def submit_complaint(self, building, complaint_type, datetime):
        
        if complaint_type == "Exhaust mati": # Jika tidak karena exhaust maka perintah else akan di jalankan
            complaint_text = f"Exhaust saya mati, di lantai {self.floor} dan unit {self.unit_number}, {self.datetime}."
        else:
            complaint_text = f"Keluhan: {complaint_type}, di lantai {self.floor} dan unit {self.unit_number}, tekirim :{self.datetime}."
        
        report_obj = Report(self.username, self.floor, self.unit_number, complaint_text, datetime)
        building.add_report(report_obj)
        print(f"\nKeluhan Anda telah diajukan: '{complaint_text}'")

class Tenant_DB(User):
    def __init__(self, username, password, floor, unit_number, datetime):
        super().__init__(username, password)
        self.floor = floor
        self.unit_number = unit_number
        


# --- Kelas Building dan Report yang sudah ada ---

class Building:
    def __init__(self, num_floors, west_units_per_floor, east_units_per_floor):
        self.num_floors = num_floors
        self.west_units_per_floor = west_units_per_floor
        self.east_units_per_floor = east_units_per_floor
        self.reports = [] # List laporan di memori
        self._next_report_id = 1
        print(f"Apartement dengan {self.num_floors} lantai.\n")

    def add_report(self, report):
        # Memastikan ID Laporan di memori sesudia dengan data yang dimuat
        if not self.reports and loaded_complaints_count > 0: # Ini hanya dipanggil sekali saat inisiasi jika ada data dari file
            self._next_report_id = loaded_complaints_count + 1 # Jaga jaga jika variable next report ini 0

        report.report_id = self._next_report_id
        self._next_report_id += 1
        self.reports.append(report)

        # Simpan laporan ke file setelah dirambahkan ke memori
        # Konversi objek Report ke dictionaru untuk disimpan di JSON
        report_data = {
            "report_id": report.report_id,
            "tenant_username": report.tenant_username,
            "floor": report.floor,
            "unit_number": report.unit_number,
            "complaint_text": report.complaint_text,
            "datetime": report.datetime,
            "expired": report.expired, "status": report.status
        }

        # Ambil semua laporan saat ini dari file, tambahkan yang baru, lalu simpan kembali
        all_complaints_from_file = load_complaints()
        all_complaints_from_file.append(report_data)
        save_complaints(all_complaints_from_file)

class Report:
    def __init__(self, tenant_username, floor, unit_number, complaint_text, expired, status):
        self.report_id = None # Akan diisi saat ditambahkan ke Building
        self.tenant_username = tenant_username
        self.floor = floor
        self.unit_number = unit_number
        self.complaint_text = complaint_text
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.expired = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        self.status = status # atribut untuk laporan






class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password) # Untuk mengakses metode dari kelas induk dalam suatu kelas turunan (subkelas)

    def view_tenant_reports(self):
        """Menampilkan laporan dari file JSON"""
        reports_from_file = load_complaints()
        print("\n--- DAFTAR LAPORAN KELUHAN JSON ---")
        if not reports_from_file:
            print("Belum ada laporan keluhan yang di ajukan")
            return

        for report_data in reports_from_file[:5]: # 5 adalah batas yang bisa di tampilkan pada terminal

            print(f"ID: {report_data['report_id']} | Tenant: {report_data['tenant_username']} | Lantai: {report_data['floor']} | Unit: {report_data['unit_number']}")
            print(f"keluhan: {report_data['complaint_text']}")
            print(f"tanggal: {report_data['datetime']}")
            print(f"batas waktu: {report_data['expired']} | Status: {report_data['status']}")
            print("-" * 40)

            status_id = input("Status on check :")
        time.sleep(2)



    def update_report_status(self):
        """Memungkinkan admin untuk memperbarui status laporan."""
        reports_from_file = load_complaints()
        if not reports_from_file:
            print("Belum ada laporan keluhan yang bisa diperbarui.")
            time.sleep(1)
            return

        print("\n--- PERBARUI STATUS LAPORAN ---")
        self.view_tenant_reports() # Tampilkan semua laporan untuk referensi
        
        try:
            report_id_to_update = int(input("Masukkan ID Laporan yang ingin diperbarui statusnya (0 untuk batal): "))
            if report_id_to_update == 0:
                print("Pembatalan pembaruan status.")
                time.sleep(1)
                return
        except ValueError:
            print("ID Laporan tidak valid. Masukkan angka.")
            time.sleep(1)
            return

        found_report = None
        for report in reports_from_file:
            if report.get('report_id') == report_id_to_update:
                found_report = report
                break

        if found_report:
            print(f"\nLaporan terpilih: ID {found_report.get('report_id')} - {found_report.get('complaint_text')}")
            print(f"Status saat ini: {found_report.get('status')}")
            
            new_status = input("Masukkan status baru (Pending/On Progress/Done): ").strip()
            # Validasi status input
            if new_status.lower() in ["pending", "on progress", "done"]:
                found_report['status'] = new_status.capitalize() # Update status
                save_complaints(reports_from_file) # Simpan perubahan ke file
                print(f"Status laporan ID {report_id_to_update} berhasil diperbarui menjadi '{new_status.capitalize()}'.")
            else:
                print("Status tidak valid. Silakan masukkan 'Pending', 'On Progress', atau 'Done'.")
        else:
            print(f"Laporan dengan ID {report_id_to_update} tidak ditemukan.")
        
        time.sleep(2)




# _=== MAIN MENU ===_

if __name__ == '__main__':
    os.system("clear")

    print("=" * 10, "Skandinavia", "=" * 10)
    print("Ketik 'DATABASE' untuk melihat akun tenant")
    print("Ketik 'LAPORAN' untuk melihat semua keluhan")
    print("Ketik 'keluar' untuk berhenti\n")

    # Muiat keluhan yang sudah ada saat program dimulai
    loaded_complaints = load_complaints()
    loaded_complaints_count = len(loaded_complaints)
    print(f"Memuat {loaded_complaints_count} keluhan dari '{COMPLAINTS_FILE}'")

    # Lantai yang tersedia
    skandi = Building(num_floors=37, west_units_per_floor=21, east_units_per_floor=16)

    # jika ada keluhan yang dimuat, pastikan _next_report_id disesuaikan
    if loaded_complaints_count > 0:
        # Temukan ID tertinggi yang sudah ada di file
        max_id = max(report['report_id'] for report in loaded_complaints)
        skandi._next_report_id = max_id = 1

    # Inisialisasi daftar Tenant     

    tenant_account = {
        "zaki_l1": Tenant("zaki_l1", "zaki123", floor=1, unit_number="1E04", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 1, East unit 04
        "nina_l2": Tenant("nina_l2", "nina456", floor=2, unit_number="2W11", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 2, West unit 11
        "aldi_l3": Tenant("aldi_l3", "aldi789", floor=3, unit_number="3E07", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 3, East unit 07
    }
    print("Lainya di database..")

    tenant_account_database = {
        "zaki_l1": Tenant_DB("zaki_l1", "zaki123", floor=1, unit_number="1E04", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 1, East unit 04
        "nina_l2": Tenant_DB("nina_l2", "nina456", floor=2, unit_number="2W11", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 2, West unit 11
        "aldi_l3": Tenant_DB("aldi_l3", "aldi789", floor=3, unit_number="3E07", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 3, East unit 07
        "tiwi_l4": Tenant_DB("tiwi_l4", "tiwi321", floor=4, unit_number="4W16", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 4, West unit 16
        "bima_l5": Tenant_DB("bima_l5", "bima555", floor=5, unit_number="5E12", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 5, East unit 12
        "salsa_l6": Tenant_DB("salsa_l6", "salsa234", floor=6, unit_number="6W03", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 6, West unit 03
        "raka_l7": Tenant_DB("raka_l7", "raka999", floor=7, unit_number="7E15", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 7, East unit 15
        "gina_l8": Tenant_DB("gina_l8", "gina101", floor=8, unit_number="8W08", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 8, West unit 08
        "yusuf_l9": Tenant_DB("yusuf_l9", "yusuf202", floor=9, unit_number="9E02", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 9, East unit 02
        "rudi_l10": Tenant_DB("rudi_l10", "pass123", floor=10, unit_number="10W05", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 10, West unit 05
        "maya_l11": Tenant_DB("maya_l11", "maya111", floor=11, unit_number="11E09", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 11, East unit 09
        "rio_l12": Tenant_DB("rio_l12", "rio777", floor=12, unit_number="12W20", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 12, West unit 20
        "siti_l13": Tenant_DB("siti_l13", "siti456", floor=13, unit_number="13E06", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 13, East unit 06
        "farid_l14": Tenant_DB("farid_l14", "farid555", floor=14, unit_number="14W14", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 14, West unit 14
        "hani_l15": Tenant_DB("hani_l15", "hani000", floor=15, unit_number="15E01", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 15, East unit 01
        "rama_l16": Tenant_DB("rama_l16", "rama666", floor=16, unit_number="16W18", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 16, West unit 18
        "rehan_l17": Tenant_DB("rehan_l17", "rehan18", floor=17, unit_number="17E19", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 17, East unit 19
        "lina_l18": Tenant_DB("lina_l18", "lina432", floor=18, unit_number="18W12", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 18, West unit 12
        "devi_l19": Tenant_DB("devi_l19", "devi300", floor=19, unit_number="19E11", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 19, East unit 11
        "kucir_l20": Tenant_DB("kucir_l20", "kucir21", floor=20, unit_number="20W03", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 20, West unit 03
        "aldi_l21": Tenant_DB("aldi_l21", "aldi123", floor=21, unit_number="21E14", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 21, East unit 14
        "bella_l22": Tenant_DB("bella_l22", "bella765", floor=22, unit_number="22W09", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 22, West unit 09
        "jamal_l23": Tenant_DB("jamal_l23", "jamal888", floor=23, unit_number="23E07", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 23, East unit 07
        "cindy_l24": Tenant_DB("cindy_l24", "cindy321", floor=24, unit_number="24W02", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 24, West unit 02
        "siti_l25": Tenant_DB("siti_l25", "siti456", floor=25, unit_number="25E12", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 25, East unit 12
        "agus_l26": Tenant_DB("agus_l26", "agus909", floor=26, unit_number="26W07", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 26, West unit 07
        "sari_l27": Tenant_DB("sari_l27", "sari321", floor=27, unit_number="27E05", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 27, East unit 05
        "budi_l28": Tenant_DB("budi_l28", "budi111", floor=28, unit_number="28W04", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 28, West unit 04
        "kiki_l29": Tenant_DB("kiki_l29", "kiki909", floor=29, unit_number="29E10", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 29, East unit 10
        "riko_l30": Tenant_DB("riko_l30", "riko212", floor=30, unit_number="30W01", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 30, West unit 01
        "vita_l31": Tenant_DB("vita_l31", "vita777", floor=31, unit_number="31E03", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 31, East unit 03
        "rafi_l32": Tenant_DB("rafi_l32", "rafi777", floor=32, unit_number="32W06", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 32, West unit 06
        "nada_l33": Tenant_DB("nada_l33", "nada001", floor=33, unit_number="33E08", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 33, East unit 08
        "danil_l34": Tenant_DB("danil_l34", "danil987", floor=34, unit_number="34W19", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 34, West unit 19
        "fira_l35": Tenant_DB("fira_l35", "fira555", floor=35, unit_number="35E06", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 35, East unit 06
        "galih_l36": Tenant_DB("galih_l36", "galih333", floor=36, unit_number="36W17", datetime=datetime.now().strftime("%Y-%m-%d")),  # Lantai 36, West unit 17
        "yuni_l37": Tenant_DB("yuni_l37", "yuni222", floor=37, unit_number="37E13", datetime=datetime.now().strftime("%Y-%m-%d"))  # Lantai 37, East unit 13
    }

    # Inisialisasi Admin
    admin_main = Admin("admin1", "password")



    # --- LOOP UTAMA INTERAKSI PENGGUNA ---
    while True:
        user_input = input("\nMasukkan perintah atau username (keluar untuk berhenti): ").strip().lower()
        
        if user_input == "keluar":
            print("Program dihentikan, Keluar..")
            break

        elif user_input == "database": # Perintah
            for username, tenant_obj in tenant_account_database.items():
                print(f"Username: {username}, Password: {tenant_obj.password}, Lantai: {tenant_obj.floor}, Unit: {tenant_obj.unit_number}")
                print("-" * 40)
                time.sleep(2)
        elif user_input == "laporan":
            print("\n-- Login Admin Melihat Laporan")
            admin_username_input = "admin1"
            admin_password_input = "password"

            if admin_main.login(admin_username_input, admin_password_input):
                admin_main.view_tenant_reports() # Admin sekarang membaca langsung
            else:
                print("Login gagal: Username atau password salah")
            time.sleep(2)
 

        elif user_input in tenant_account :
            current_tenant = tenant_account[user_input]
            tenant_password = input(f"Masukan password '{current_tenant.username}':")
            if current_tenant.login(current_tenant.username, tenant_password):
                print(f"\nLogin berhasil! {current_tenant.username}")
                complaint_text = input("Masukan keluhan anda (ex: Exhaust Mati) :")
                
                current_tenant.submit_complaint(skandi, complaint_text, datetime) # Logika submit complaint
            else:
                print("Password Salah")

        else:
            print("Perintah atau username belum ada. Silahkan coba lagi")
            time.sleep(1)
