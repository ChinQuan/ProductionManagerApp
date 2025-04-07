def calculate_average_time(df):
    st.header("⏳ Average Production Time Analysis")

    if df.empty:
        st.write("No data available to calculate average production time.")
        return

    if 'Date' not in df.columns:
        st.write("Date column not found in data.")
        return

    # Konwersja kolumny 'Date' do formatu datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # 📅 Opcje wyboru przedziału czasowego
    st.sidebar.header("📅 Filter by Date Range")
    date_filter = st.sidebar.selectbox(
        "Select Date Range",
        ["Last Week", "Last Month", "Last Year", "Custom Range"]
    )

    if date_filter == "Last Week":
        start_date = datetime.now() - timedelta(weeks=1)
        end_date = datetime.now()
    elif date_filter == "Last Month":
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif date_filter == "Last Year":
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
    else:
        start_date = st.sidebar.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        end_date = st.sidebar.date_input("End Date", value=datetime.now())
    
    # Filtrujemy dane na podstawie wybranego przedziału czasowego
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    # **Nowa funkcjonalność: Filtrujemy tylko dni robocze (poniedziałek - piątek)**
    working_days_df = filtered_df[filtered_df['Date'].dt.dayofweek < 5]  # 0 = Poniedziałek, ..., 4 = Piątek

    if working_days_df.empty:
        st.write("❌ No data available for the selected date range (Working Days Only).")
        return

    st.write(f"Showing data from **{start_date.date()}** to **{end_date.date()}** (Working Days Only)")

    # 📌 Wyświetl przefiltrowane dane jako tabelę do debugowania
    st.write("### Debug: Filtered DataFrame (Working Days Only)")
    st.dataframe(working_days_df)

    # Przykład wyświetlania ilości danych i liczby unikalnych dat
    st.write(f"Total rows: {len(working_days_df)}")
    st.write(f"Unique dates: {working_days_df['Date'].nunique()}")
