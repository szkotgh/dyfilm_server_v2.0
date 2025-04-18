import qrcode

qr = qrcode.make(
    data='https://film.szk.kr',
    version=1,
    box_size=1,
    border=2,
    error_correction=qrcode.ERROR_CORRECT_L,
)
qr.save('qr.png')
