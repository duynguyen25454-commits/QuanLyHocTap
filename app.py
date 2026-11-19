
import sqlite3
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# Kết nối cơ sở dữ liệu
def get_db_connection():
    conn = sqlite3.connect("database/quanly.db")
    conn.row_factory = sqlite3.Row
    return conn

# Tạo bảng sinh viên
def tao_bang_sinh_vien():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sinh_vien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sv TEXT UNIQUE NOT NULL,
            ho_ten TEXT NOT NULL,
            ngay_sinh TEXT,
            gioi_tinh TEXT,
            email TEXT,
            so_dien_thoai TEXT
        )
    """)

    conn.commit()
    conn.close()
# Tạo bảng môn học
def tao_bang_mon_hoc():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS mon_hoc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_mon TEXT UNIQUE NOT NULL,
            ten_mon TEXT NOT NULL,
            so_tin_chi INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()
def tao_bang_diem():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS diem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sinh_vien_id INTEGER NOT NULL,
            mon_hoc_id INTEGER NOT NULL,
            diem_chuyen_can REAL,
            diem_giua_ky REAL,
            diem_cuoi_ky REAL,

            UNIQUE(sinh_vien_id, mon_hoc_id),

            FOREIGN KEY (sinh_vien_id)
                REFERENCES sinh_vien(id),

            FOREIGN KEY (mon_hoc_id)
                REFERENCES mon_hoc(id)
        )
    """)

    conn.commit()
    conn.close()
# Trang tổng quan
@app.route("/")
def trang_chu():
    conn = get_db_connection()

    tong_sinh_vien = conn.execute(
        "SELECT COUNT(*) FROM sinh_vien"
    ).fetchone()[0]

    tong_mon_hoc = conn.execute(
        "SELECT COUNT(*) FROM mon_hoc"
    ).fetchone()[0]

    diem_trung_binh = conn.execute("""
        SELECT AVG(
            ((diem_chuyen_can + diem_giua_ky * 2) / 3) * 0.4
            + diem_cuoi_ky * 0.6
        )
        FROM diem
    """).fetchone()[0]

    sinh_vien_can_chu_y = conn.execute("""
        SELECT COUNT(*)
        FROM diem
        WHERE (
            ((diem_chuyen_can + diem_giua_ky * 2) / 3) * 0.4
            + diem_cuoi_ky * 0.6
        ) < 4
    """).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        tong_sinh_vien=tong_sinh_vien,
        tong_mon_hoc=tong_mon_hoc,
        diem_trung_binh=round(diem_trung_binh or 0, 2),
        sinh_vien_can_chu_y=sinh_vien_can_chu_y
    )
@app.route("/sinh-vien")
def danh_sach_sinh_vien():
    conn = get_db_connection()
    sinh_viens = conn.execute(
        "SELECT * FROM sinh_vien ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "sinh_vien.html",
        sinh_viens=sinh_viens
    )

@app.route("/them-sinh-vien", methods=["POST"])
def them_sinh_vien():
    from flask import request, redirect, url_for

    ma_sv = request.form.get("ma_sv", "").strip()
    ho_ten = request.form.get("ho_ten", "").strip()
    ngay_sinh = request.form.get("ngay_sinh", "")
    gioi_tinh = request.form.get("gioi_tinh", "")
    email = request.form.get("email", "").strip()
    so_dien_thoai = request.form.get("so_dien_thoai", "").strip()

    if not ma_sv or not ho_ten:
        return "Vui lòng nhập mã sinh viên và họ tên", 400

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO sinh_vien
            (ma_sv, ho_ten, ngay_sinh, gioi_tinh, email, so_dien_thoai)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ma_sv, ho_ten, ngay_sinh, gioi_tinh, email, so_dien_thoai))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Mã sinh viên đã tồn tại!", 400
    finally:
        conn.close()

    return redirect(url_for("danh_sach_sinh_vien"))
@app.route("/sua-sinh-vien/<int:id>")
def form_sua_sinh_vien(id):
    conn = get_db_connection()

    sinh_vien = conn.execute(
        "SELECT * FROM sinh_vien WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if sinh_vien is None:
        return "Không tìm thấy sinh viên!", 404

    return render_template(
        "sua_sinh_vien.html",
        sv=sinh_vien
    )
@app.route("/xoa-sinh-vien/<int:id>", methods=["POST"])
def xoa_sinh_vien(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM sinh_vien WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("danh_sach_sinh_vien"))
@app.route("/sua-sinh-vien/<int:id>", methods=["POST"])
def sua_sinh_vien(id):
    from flask import request

    ma_sv = request.form.get("ma_sv", "").strip()
    ho_ten = request.form.get("ho_ten", "").strip()
    ngay_sinh = request.form.get("ngay_sinh", "")
    gioi_tinh = request.form.get("gioi_tinh", "")
    email = request.form.get("email", "").strip()
    so_dien_thoai = request.form.get("so_dien_thoai", "").strip()

    if not ma_sv or not ho_ten:
        return "Vui lòng nhập mã sinh viên và họ tên!", 400

    conn = get_db_connection()

    conn.execute("""
        UPDATE sinh_vien
        SET ma_sv = ?,
            ho_ten = ?,
            ngay_sinh = ?,
            gioi_tinh = ?,
            email = ?,
            so_dien_thoai = ?
        WHERE id = ?
    """, (
        ma_sv,
        ho_ten,
        ngay_sinh,
        gioi_tinh,
        email,
        so_dien_thoai,
        id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("danh_sach_sinh_vien"))
# Trang quản lý môn học
@app.route("/mon-hoc")
def danh_sach_mon_hoc():
    conn = get_db_connection()

    mon_hocs = conn.execute(
        "SELECT * FROM mon_hoc ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "mon_hoc.html",
        mon_hocs=mon_hocs
    )
# Thêm môn học
@app.route("/them-mon-hoc", methods=["POST"])
def them_mon_hoc():
    ma_mon = request.form.get("ma_mon", "").strip().upper()
    ten_mon = request.form.get("ten_mon", "").strip()
    so_tin_chi = request.form.get("so_tin_chi", "").strip()

    if not ma_mon or not ten_mon or not so_tin_chi:
        return "Vui lòng nhập đầy đủ thông tin môn học!", 400

    try:
        so_tin_chi = int(so_tin_chi)

        if so_tin_chi <= 0:
            return "Số tín chỉ phải lớn hơn 0!", 400

    except ValueError:
        return "Số tín chỉ không hợp lệ!", 400

    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO mon_hoc (ma_mon, ten_mon, so_tin_chi)
            VALUES (?, ?, ?)
            """,
            (ma_mon, ten_mon, so_tin_chi)
        )

        conn.commit()

    except sqlite3.IntegrityError:
        return "Mã môn học đã tồn tại!", 400

    finally:
        conn.close()

    return redirect(url_for("danh_sach_mon_hoc"))

# Xóa môn học
@app.route("/xoa-mon-hoc/<int:id>", methods=["POST"])
def xoa_mon_hoc(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM mon_hoc WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("danh_sach_mon_hoc"))
@app.route("/diem")
def danh_sach_diem():
    conn = get_db_connection()

    sinh_viens = conn.execute("""
        SELECT * FROM sinh_vien
        ORDER BY ma_sv
    """).fetchall()

    mon_hocs = conn.execute("""
        SELECT * FROM mon_hoc
        ORDER BY ma_mon
    """).fetchall()

    ds_diem = conn.execute("""
        SELECT
            diem.id,
            sinh_vien.ma_sv,
            sinh_vien.ho_ten,
            mon_hoc.ma_mon,
            mon_hoc.ten_mon,
            diem.diem_chuyen_can,
diem.diem_giua_ky,
diem.diem_cuoi_ky,

ROUND(
    (
        (diem.diem_chuyen_can +
        diem.diem_giua_ky * 2) / 3
    ) * 0.4
    +
    diem.diem_cuoi_ky * 0.6,
    2
) AS diem_tong_ket
        FROM diem
        JOIN sinh_vien ON diem.sinh_vien_id = sinh_vien.id
        JOIN mon_hoc ON diem.mon_hoc_id = mon_hoc.id
        ORDER BY sinh_vien.ma_sv
    """).fetchall()

    conn.close()

    return render_template(
    "diem.html",
    sinh_viens=sinh_viens,
    mon_hocs=mon_hocs,
    ds_diem=ds_diem
)

@app.route("/them-diem", methods=["POST"])
def them_diem():
    sinh_vien_id = request.form.get("sinh_vien_id")
    mon_hoc_id = request.form.get("mon_hoc_id")

    diem_chuyen_can = request.form.get("diem_chuyen_can")
    diem_giua_ky = request.form.get("diem_giua_ky")
    diem_cuoi_ky = request.form.get("diem_cuoi_ky")

    try:
        diem_chuyen_can = float(diem_chuyen_can)
        diem_giua_ky = float(diem_giua_ky)
        diem_cuoi_ky = float(diem_cuoi_ky)

        if not all(0 <= d <= 10 for d in [
            diem_chuyen_can,
            diem_giua_ky,
            diem_cuoi_ky
        ]):
            return redirect(url_for("danh_sach_diem"))

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO diem (
                sinh_vien_id,
                mon_hoc_id,
                diem_chuyen_can,
                diem_giua_ky,
                diem_cuoi_ky
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            sinh_vien_id,
            mon_hoc_id,
            diem_chuyen_can,
            diem_giua_ky,
            diem_cuoi_ky
        ))

        conn.commit()
        conn.close()

    except (ValueError, TypeError, sqlite3.IntegrityError):
        return redirect(url_for("danh_sach_diem"))

    return redirect(url_for("danh_sach_diem"))

@app.route("/thong-ke")
def thong_ke():
    conn = get_db_connection()

    tong_sinh_vien = conn.execute(
        "SELECT COUNT(*) FROM sinh_vien"
    ).fetchone()[0]

    tong_mon_hoc = conn.execute(
        "SELECT COUNT(*) FROM mon_hoc"
    ).fetchone()[0]

    tong_luot_diem = conn.execute(
        "SELECT COUNT(*) FROM diem"
    ).fetchone()[0]

    diem_trung_binh = conn.execute("""
        SELECT ROUND(AVG(
            ((diem_chuyen_can + diem_giua_ky * 2) / 3.0) * 0.4
            + diem_cuoi_ky * 0.6
        ), 2)
        FROM diem
    """).fetchone()[0]
    thong_ke_mon_hoc = conn.execute("""
        SELECT
            mon_hoc.ten_mon,
            ROUND(AVG(
                ((diem.diem_chuyen_can +
                diem.diem_giua_ky * 2) / 3.0) * 0.4
                + diem.diem_cuoi_ky * 0.6
            ), 2) AS diem_trung_binh
        FROM diem
        JOIN mon_hoc ON diem.mon_hoc_id = mon_hoc.id
        GROUP BY mon_hoc.id, mon_hoc.ten_mon
        ORDER BY mon_hoc.ten_mon
    """).fetchall()
    thong_ke_mon_hoc = [
    {
        "ten_mon": row["ten_mon"],
        "diem_trung_binh": float(row["diem_trung_binh"])
    }
    for row in thong_ke_mon_hoc
]
    conn.close()

    return render_template(
        "thong_ke.html",
        tong_sinh_vien=tong_sinh_vien,
        tong_mon_hoc=tong_mon_hoc,
        tong_luot_diem=tong_luot_diem,
        diem_trung_binh=diem_trung_binh,
        thong_ke_mon_hoc=thong_ke_mon_hoc
    )
@app.route("/tinh-diem-muc-tieu")
def tinh_diem_muc_tieu():
    return render_template("tinh_diem_muc_tieu.html")
if __name__ == "__main__":

    tao_bang_sinh_vien()
    tao_bang_mon_hoc()
    tao_bang_diem()
    app.run(debug=True)
