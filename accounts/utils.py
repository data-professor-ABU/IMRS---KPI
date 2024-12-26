from pathlib import Path

import pandas as pd
from django.conf import settings


def analyze_users_attendance_data(file_path, month_work_minutes=540, daily_rate=20):
    # Excel faylini yuklash
    data = pd.ExcelFile(file_path, engine="openpyxl")  # pip install openpyxl

    # Fayldagi birinchi sheetni olish
    df = data.parse(data.sheet_names[0])

    # Ustunlarni qayta nomlash
    df.columns = ["ID", "Name", "Device", "EntryType", "Timestamp"]

    # Timestamp tozalash va formati
    df = df.dropna(subset=["Timestamp"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Ish vaqti chegaralari
    work_start = pd.Timestamp("09:00:00").time()
    work_end = pd.Timestamp("18:00:00").time()

    # Barcha foydalanuvchilar uchun summary yaratish
    summary_list = []

    # Har bir foydalanuvchi uchun tahlil qilish
    for user_name in df["Name"].unique():
        # Foydalanuvchi ma'lumotlarini olish
        user_data = df[df["Name"] == user_name]

        # Kechikish (lateness) hisoblash
        entry_data = user_data[user_data["Device"].str.contains("Kirish", na=False)]
        entry_data["Date"] = entry_data["Timestamp"].dt.date
        latest_entries = entry_data.groupby("Date")["Timestamp"].min()
        lateness_minutes = latest_entries.apply(
            lambda x: max(
                (x.time().hour * 60 + x.time().minute)
                - (work_start.hour * 60 + work_start.minute),
                0,
            )
        ).astype(
            int
        )  # Int tipiga aylantirish

        # Erta chiqish (early exit) hisoblash
        exit_data = user_data[user_data["Device"].str.contains("Chiqish", na=False)]
        exit_data["Date"] = exit_data["Timestamp"].dt.date
        last_exits = exit_data.groupby("Date")["Timestamp"].max()
        early_exit_minutes = last_exits.apply(
            lambda x: max(
                (work_end.hour * 60 + work_end.minute)
                - (x.time().hour * 60 + x.time().minute),
                0,
            )
        ).astype(
            int
        )  # Int tipiga aylantirish

        # Natijalarni birlashtirish
        user_summary = pd.DataFrame(
            {
                "Name": user_name,
                "Date": lateness_minutes.index,
                "MinutesLate": lateness_minutes.values,
                "MinutesEarlyExit": early_exit_minutes.reindex(
                    lateness_minutes.index, fill_value=0
                ).values,
                "TotalMinutes": (
                    lateness_minutes.values
                    + early_exit_minutes.reindex(
                        lateness_minutes.index, fill_value=0
                    ).values
                ).astype(
                    int
                ),  # Sonlarga aylantirib qo'shish
            }
        )

        summary_list.append(user_summary)

    # Barcha foydalanuvchilar uchun umumiy summary
    final_summary = pd.concat(summary_list)
    # Yangi ustunni formulaga asoslanib qo'shish
    final_summary["Jarima_ball"] = (
        final_summary["TotalMinutes"] / month_work_minutes
    ) * daily_rate

    return final_summary
