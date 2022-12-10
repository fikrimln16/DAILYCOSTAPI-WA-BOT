from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from database import SessionLocal
from datetime import datetime 
from pytz import timezone
import os

app = Flask(__name__)



@app.route("/")
def hello():
    return "Hello Worlda"

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body')
    response = MessagingResponse()
    print(incoming_msg)
    message = response.message()
    responded = False
    words = incoming_msg.split('@')

    
    if "hello" in incoming_msg:
        rep = "Hello Fikri, selamat datang di bot keuangan buatan Fikri.\n\n"\
            "*. ketik 'help' untuk melihat fitur-fitur .*\n"\
            "=====================================\n"
        message.body(rep)
        responded = True

    if "cek uang" in incoming_msg:
        db = get_db()
        tabungan = db.execute("SELECT uang_gopay, uang_cash, uang_rekening FROM tabungan").fetchall()
        for row in tabungan:
            uanggopay = row[0]
            uangcash = row[1]
            uangrekening = row[2]
            reminder_string = "\nUang anda tersisa : \n\n"\
                "GOPAY = {}.\n"\
                    "CASH = {}.\n"\
                        "REKENING = {}.".format(uanggopay, uangcash, uangrekening)
            message.body(reminder_string)
            responded = True
            db.close()

    if "pengeluaran hari ini" in incoming_msg:
            datenow = datetime.now(timezone('Asia/Jakarta'))
            tanggal = datenow.strftime('%Y-%m-%d')
            db = get_db()
            row = db.execute("SELECT nama, jumlah, tanggal, pembayaran FROM pengeluaran WHERE tanggal BETWEEN '{} 00:00:00' AND '{} 23:59:59'".format(tanggal, tanggal)).fetchall()
            for i in row:
                reply = "Barang yang dibeli pada tanggal {} : \n\n"\
                            "nama barang : {} \n"\
                                "harga barang : {} \n"\
                                    "tanggal beli : {} \n"\
                                        "pembayaran : {}".format(tanggal, i[0], i[1], i[2], i[3])
                message.body(reply)
                responded = True

    if "deposit uang" in incoming_msg:
        reminder_string = "Berikut adalah tata cara untuk deposito uang.\n\n"\
            "1. Pilih tabungan GOPAY/CASH/REKENING.\n"\
                "2. Ketik di chat [TABUNGAN]@[UANG]."
        message.body(reminder_string)
        responded = True

    if "bulan" in incoming_msg:
        db = get_db()
        pengeluaran = db.execute("SELECT SUM(jumlah) as 'jumlah', COUNT(jumlah) as 'total' FROM pengeluaran").fetchall()
        for row in pengeluaran:
            totalharga = row[0]
            jumlahbarang = row[1]
        reminder_string = "Berikut adalah pengeluaran anda bulan ini.\n\n"\
            "1. Total harga yang anda beli : {}.\n"\
                "2. Total barang yang anda beli : {}.".format(totalharga, jumlahbarang)
        message.body(reminder_string)
        responded = True
        db.close()

    if "beli barang" in incoming_msg:
        reminder_string = "Berikut adalah tata cara untuk membeli barang.\n\n"\
            "1. Format BELI@[PEMBAYARAN]@[HARGA]@[NAMA_BARANG].\n"\
                "2. Ketik di chat lalu enter."
        message.body(reminder_string)
        responded = True


    if "help" in incoming_msg:
        reminder_string = "Berikut adalah tata cara untuk membeli barang.\n\n"\
            "1. cek uang : tinggal ketik 'cek uang'.\n"\
                "2. deposito uang : tinggal ketik 'deposit uang'.\n"\
                    "3. pengeluaran bulanan : tinggal ketik 'bulan'.\n"\
                        "4. beli barang : tinggal ketik 'beli barang'"
        message.body(reminder_string)
        responded = True
    
    if len(words) == 1 and "no" in incoming_msg:
        reply = "OK, Have a nice day!"
        message.body(reply)
        responded = True


    elif len(words) != 1:
        input_type = words[0].strip()
        input_string = words[1].strip()
        if input_type == "GOPAY":

            db = get_db()
            saldoawalgopay = db.execute("SELECT uang_gopay FROM tabungan").fetchone()
            for i in saldoawalgopay:
                saldogopay = i
            db.close()

            tambahuanggopay = int(input_string)
            saldoakhirgopay = saldogopay + tambahuanggopay
            db.execute("UPDATE tabungan SET uang_gopay = {} WHERE user_id = 1".format(saldoakhirgopay))
            db.commit()

            reply="Berhasil memasukkan GOPAY"
            printout(input_string)
            message.body(reply)
            responded = True

        if input_type == "CASH":

            db = get_db()
            saldoawalcash = db.execute("SELECT uang_cash FROM tabungan").fetchone()
            for i in saldoawalcash:
                saldocash = i
            db.close()

            tambahuangcash = int(input_string)
            saldoakhircash = saldocash + tambahuangcash
            db.execute("UPDATE tabungan SET uang_cash = {} WHERE user_id = 1".format(saldoakhircash))
            db.commit()
            
            printout(input_string)
            reply="Berhasil memasukkan CASH"
            message.body(reply)
            responded = True

        if input_type == "REKENING":

            db = get_db()
            saldoawalrekening = db.execute("SELECT uang_rekening FROM tabungan").fetchone()
            for i in saldoawalrekening:
                saldorekening = i
            db.close()

            tambahuangrekening = int(input_string)
            saldoakhirrekening = saldorekening + tambahuangrekening
            db.execute("UPDATE tabungan SET uang_rekening = {} WHERE user_id = 1".format(saldoakhirrekening))
            db.commit()
            
            reply="Berhasil memasukkan REKENING"
            message.body(reply)
            printout(input_string)
            responded = True

        if input_type == "BELI":
            input_harga = words[2].strip()
            input_barang = words[3].strip()

            if input_string == "GOPAY":
                db = get_db()
                saldoawalgopay = db.execute("SELECT uang_gopay FROM tabungan").fetchone()
                for i in saldoawalgopay:
                    saldogopay = i
                db.close()
                printout(input_barang)
                pengurangan = int(input_harga)
                saldoakhirgopay = saldogopay - pengurangan
                db.execute("UPDATE tabungan SET uang_gopay = {} WHERE user_id = 1".format(saldoakhirgopay))
                db.commit()
                db.close()

            if input_string == "CASH":
                db = get_db()
                saldoawalcash = db.execute("SELECT uang_cash FROM tabungan").fetchone()
                for i in saldoawalcash:
                    saldocash = i
                db.close()

                pengurangancash = int(input_harga)
                saldoakhircash = saldocash - pengurangancash
                db.execute("UPDATE tabungan SET uang_cash = {} WHERE user_id = 1".format(saldoakhircash))
                db.commit()
                db.close()

            if input_string == "REKENING":
                db = get_db()
                saldoawalrekening = db.execute("SELECT uang_rekening FROM tabungan").fetchone()
                for i in saldoawalrekening:
                    saldorekening = i
                db.close()

                penguranganrekening = int(input_harga)
                saldoakhirrekening = saldorekening - penguranganrekening
                db.execute("UPDATE tabungan SET uang_rekening = {} WHERE user_id = 1".format(saldoakhirrekening))
                db.commit()
                db.close()

            reply="Berhasil memasukkan inputan"
            message.body(reply)
            responded = True
            x = datetime.now(timezone('Asia/Jakarta'))
            db.execute("INSERT INTO pengeluaran VALUES(null, '{}', '{}', {}, '{}', 1 )".format(input_barang, x, int(input_harga), input_string))
            db.commit()


        if not responded:
            message.body("Incorect reequst format")

    return str(response)


def printout(msg):
    return msg


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))