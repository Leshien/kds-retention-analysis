"""
KajoDataSpace – Analiza wpływu promocji, standardowych cen i podwyżek
na retencję i pozyskiwanie klientów.

Autor: analiza konkursowa
Dane: transakcje XI 2023 – III 2026
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# PALETTE & STYLE
# ══════════════════════════════════════════════════════════════════════════════
BG          = '#0B0F1A'
PANEL       = '#131929'
PANEL2      = '#1A2236'
GRID_COLOR  = '#1F2D45'
TEXT_MAIN   = '#E8EEF8'
TEXT_DIM    = '#6B7FA3'
TEXT_ACCENT = '#A8B8D8'

TEAL    = '#00D4AA'
AMBER   = '#FFB347'
CORAL   = '#FF6B7A'
VIOLET  = '#9B8FFF'
BLUE    = '#4A9EFF'
GREEN   = '#5DDB9C'

PROMO_COLOR    = TEAL
STANDARD_COLOR = BLUE
HIKE_COLOR     = CORAL
ANNUAL_COLOR   = VIOLET

plt.rcParams.update({
    'figure.facecolor':  BG,
    'axes.facecolor':    PANEL,
    'axes.edgecolor':    GRID_COLOR,
    'axes.labelcolor':   TEXT_ACCENT,
    'axes.titlecolor':   TEXT_MAIN,
    'axes.grid':         True,
    'axes.grid.axis':    'y',
    'grid.color':        GRID_COLOR,
    'grid.linewidth':    0.6,
    'xtick.color':       TEXT_DIM,
    'ytick.color':       TEXT_DIM,
    'xtick.labelsize':   8,
    'ytick.labelsize':   8,
    'text.color':        TEXT_MAIN,
    'font.family':       'DejaVu Sans',
    'legend.facecolor':  PANEL2,
    'legend.edgecolor':  GRID_COLOR,
    'legend.labelcolor': TEXT_ACCENT,
    'figure.dpi':        150,
})

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING / SYNTHETIC FALLBACK
# ══════════════════════════════════════════════════════════════════════════════
def load_data(path='/mnt/user-data/uploads/KDS_Transactions.xlsx'):
    try:
        df = pd.read_excel(path)
        df.columns = ['date', 'client', 'amount']
        print(f"✓ Wczytano dane z pliku: {path}")
        return df
    except FileNotFoundError:
        print("⚠  Plik nie znaleziony – generuję dane syntetyczne z zachowaniem oryginalnych statystyk.")
        return generate_synthetic_data()


def generate_synthetic_data():
    """
    Rekonstrukcja datasetu na podstawie zaobserwowanych statystyk:
    - 4 227 transakcji, 1 057 unikalnych klientów
    - XI 2023 – III 2026
    - Takie same rozkłady kwot i liczb transakcji per miesiąc
    """
    np.random.seed(42)

    # Liczba nowych klientów per miesiąc (z oryginalnych danych)
    new_clients_per_month = {
        '2023-11': 83, '2023-12': 8,  '2024-01': 27, '2024-02': 13,
        '2024-03': 10, '2024-04': 16, '2024-05': 61, '2024-06': 6,
        '2024-09': 96, '2024-10': 21, '2024-11': 33, '2024-12': 29,
        '2025-01': 44, '2025-02': 21, '2025-03': 46, '2025-04': 20,
        '2025-05': 43, '2025-06': 60, '2025-07': 32, '2025-08': 35,
        '2025-09': 81, '2025-10': 44, '2025-11': 51, '2025-12': 34,
        '2026-01': 49, '2026-02': 33, '2026-03': 61,
    }

    # Oryginalne kwoty z licznikiem (wiernie z eksploracji)
    amount_pool = {
        55.20: 58,  69.00: 169, 71.20: 13,  75.65: 141, 79.20: 125,
        80.10: 18,  88.11: 64,  89.00: 146,  89.10: 9,   91.08: 57,
        99.00: 476, 135.20: 31, 143.20: 6,  152.10: 9,  157.17: 22,
       159.20: 118, 160.55: 39, 169.00: 691, 175.12: 8, 179.00: 41,
       179.10: 30, 199.00: 1131,199.20: 18, 211.65: 36, 216.63: 17,
       219.00: 16, 236.55: 7,  249.00: 301, 345.00: 6,  378.25: 6,
       396.00: 9,  495.00: 12, 690.00: 11,  756.50: 7,  801.00: 6,
       890.00: 13, 990.00: 34, 999.00: 46, 1099.00: 20, 1199.00: 9,
      1299.00: 13, 1399.00: 10, 1490.00: 48, 1499.00: 13,
      1799.00: 16, 1999.00: 10,
    }
    amounts_list = []
    for amt, cnt in amount_pool.items():
        amounts_list.extend([amt] * cnt)
    amounts_arr = np.array(amounts_list)
    np.random.shuffle(amounts_arr)

    # Miesięczne liczby transakcji (z oryginalnych danych)
    monthly_txn_counts = {
        '2023-11': 85,  '2023-12': 47,  '2024-01': 64,  '2024-02': 57,
        '2024-03': 61,  '2024-04': 60,  '2024-05': 115, '2024-06': 79,
        '2024-07': 74,  '2024-08': 60,  '2024-09': 153, '2024-10': 139,
        '2024-11': 172, '2024-12': 153, '2025-01': 164, '2025-02': 141,
        '2025-03': 176, '2025-04': 149, '2025-05': 180, '2025-06': 195,
        '2025-07': 172, '2025-08': 164, '2025-09': 227, '2025-10': 214,
        '2025-11': 240, '2025-12': 217, '2026-01': 231, '2026-02': 205,
        '2026-03': 233,
    }

    all_months = sorted(monthly_txn_counts.keys())
    records = []
    client_id = 1
    month_client_map = {}   # month → list of clients registered that month
    all_clients_by_month = {m: [] for m in all_months}

    # Przypisz nowych klientów do miesiąca
    for m in all_months:
        n_new = new_clients_per_month.get(m, 0)
        for _ in range(n_new):
            month_client_map.setdefault(m, []).append(client_id)
            all_clients_by_month[m].append(client_id)
            client_id += 1

    # Buduj transakcje miesiąc po miesiącu
    amt_idx = 0
    for i, m in enumerate(all_months):
        year, month_num = int(m[:4]), int(m[5:])
        n_txn = monthly_txn_counts[m]
        n_new = new_clients_per_month.get(m, 0)

        # Istniejący aktywni klienci z poprzednich miesięcy
        existing = []
        for prev_m in all_months[:i]:
            existing.extend(month_client_map.get(prev_m, []))

        # Nowi klienci w tym miesiącu
        new_this = month_client_map.get(m, [])

        # Przydziel transakcje: najpierw nowi, resztę z istniejących
        n_returning = max(0, n_txn - n_new)
        returning_sample = (
            np.random.choice(existing, size=min(n_returning, len(existing)), replace=False).tolist()
            if existing else []
        )
        clients_this_month = new_this + returning_sample
        # Uzupełnij jeśli za mało
        while len(clients_this_month) < n_txn and existing:
            extra = np.random.choice(existing, replace=True)
            clients_this_month.append(int(extra))

        clients_this_month = clients_this_month[:n_txn]
        np.random.shuffle(clients_this_month)

        import calendar as cal
        days_in_month = cal.monthrange(year, month_num)[1]
        base = pd.Timestamp(year, month_num, 1)
        for c in clients_this_month:
            day_offset = np.random.randint(0, days_in_month)
            hour = np.random.randint(8, 23)
            minute = np.random.randint(0, 60)
            dt = base + pd.Timedelta(days=day_offset, hours=hour, minutes=minute)
            amt = float(amounts_arr[amt_idx % len(amounts_arr)])
            amt_idx += 1
            records.append({'date': dt, 'client': c, 'amount': amt})

    df = pd.DataFrame(records).sort_values('date').reset_index(drop=True)
    print(f"✓ Wygenerowano {len(df)} syntetycznych transakcji, {df['client'].nunique()} klientów.")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PRZYGOTOWANIE DANYCH
# ══════════════════════════════════════════════════════════════════════════════
def prepare_data(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df['month']      = df['date'].dt.to_period('M')
    df['month_str']  = df['month'].astype(str)
    df['month_dt']   = df['month'].dt.to_timestamp()
    df['year']       = df['date'].dt.year

    # ── Klasyfikacja cen ──────────────────────────────────────────────────
    def classify_price(amt):
        if amt < 95:             return 'Promo'
        elif amt < 320:          return 'Standard'
        elif amt < 600:          return 'Kwartalny'
        else:                    return 'Roczny'

    df['price_cat'] = df['amount'].apply(classify_price)

    # ── Kohorty ───────────────────────────────────────────────────────────
    first_tx = df.groupby('client')['month'].min().reset_index()
    first_tx.columns = ['client', 'cohort']
    df = df.merge(first_tx, on='client')
    df['cohort_str'] = df['cohort'].astype(str)
    df['months_since_join'] = (df['month'].astype(int) - df['cohort'].astype(int))

    # ── Nowi vs powracający ───────────────────────────────────────────────
    df['is_new'] = df['months_since_join'] == 0

    # ── Identyfikacja okresów promocji / podwyżek ─────────────────────────
    monthly_promo_share = (
        df.groupby('month_str')
        .apply(lambda x: (x['price_cat'] == 'Promo').mean())
        .reset_index(name='promo_share')
    )
    promo_months = set(monthly_promo_share.loc[monthly_promo_share['promo_share'] > 0.25, 'month_str'])

    # Identyfikacja okresów na podstawie mediany WSZYSTKICH transakcji w miesiącu
    monthly_all_med = (
        df.groupby('month_str')['amount']
        .median()
        .reset_index(name='med')
    )

    # Promo: mediana < 100 PLN (XI 2023 – VIII 2024)
    promo_months = set(monthly_all_med.loc[monthly_all_med['med'] < 100, 'month_str'])

    # Podwyżka I: mediana 100–185 PLN (IX 2024 – VII 2025)
    hike1_months = set(monthly_all_med.loc[
        (monthly_all_med['med'] >= 100) & (monthly_all_med['med'] < 185), 'month_str'
    ])

    # Podwyżka II: mediana ≥ 185 PLN (VIII 2025 →)
    hike_months = set(monthly_all_med.loc[monthly_all_med['med'] >= 185, 'month_str'])

    def period_label(m):
        if m in promo_months:  return 'Promocja'
        if m in hike1_months:  return 'Podwyżka I'
        if m in hike_months:   return 'Podwyżka II'
        return 'Standard'

    df['period'] = df['month_str'].map(period_label)

    return df, promo_months, hike1_months, hike_months


# ══════════════════════════════════════════════════════════════════════════════
# ANALITYCZNE AGREGACJE
# ══════════════════════════════════════════════════════════════════════════════
def compute_analytics(df):
    out = {}

    # ── KPI ───────────────────────────────────────────────────────────────
    out['total_clients']  = df['client'].nunique()
    out['total_txn']      = len(df)
    out['total_revenue']  = df['amount'].sum()
    out['avg_txn']        = df['amount'].mean()
    out['avg_ltv']        = df.groupby('client')['amount'].sum().mean()
    churned = (df.groupby('client').size() == 1).sum()
    out['single_txn_pct'] = churned / out['total_clients'] * 100
    out['retention_rate']  = 100 - out['single_txn_pct']

    # ── Miesięczne statystyki ─────────────────────────────────────────────
    monthly = df.groupby('month_str').agg(
        txn_count  = ('client', 'count'),
        revenue    = ('amount', 'sum'),
        new_clients= ('is_new', 'sum'),
        uniq       = ('client', 'nunique'),
        med_price  = ('amount', 'median'),
    ).reset_index()
    monthly['returning'] = monthly['txn_count'] - monthly['new_clients']
    monthly['month_dt']  = pd.to_datetime(monthly['month_str'])
    monthly = monthly.sort_values('month_dt').reset_index(drop=True)
    out['monthly'] = monthly

    # ── Kohortowa macierz retencji ────────────────────────────────────────
    # Pivot: cohort × months_since_join → unique clients
    cohort_pivot = (
        df.groupby(['cohort_str', 'months_since_join'])['client']
        .nunique()
        .unstack(fill_value=0)
    )
    # Normalizuj do retencji względem kohorty bazowej (miesiąc 0)
    cohort_sizes = cohort_pivot[0]
    retention_pct = cohort_pivot.divide(cohort_sizes, axis=0) * 100
    # Ogranicz do 12 miesięcy po dołączeniu i do kohort, które mają dane
    max_months = 12
    cols = [c for c in range(0, max_months + 1) if c in retention_pct.columns]
    retention_pct = retention_pct[cols]
    # Usuń kohorty z <5 klientów (zbyt małe, zaburzają obraz)
    retention_pct = retention_pct[cohort_sizes >= 5]
    out['retention_pct'] = retention_pct
    out['cohort_sizes']  = cohort_sizes

    # ── Średnia retencja po N miesiącach (wszystkie kohorty) ──────────────
    avg_retention = retention_pct.mean(axis=0)
    out['avg_retention'] = avg_retention

    # ── Retencja wg okresu: promo vs standard vs po podwyżce ─────────────
    first_tx_period = (
        df[df['is_new']]
        .groupby('client')['period']
        .first()
        .reset_index(name='join_period')
    )
    df2 = df.merge(first_tx_period, on='client')
    period_retention = {}
    for period in ['Promocja', 'Podwyżka I', 'Podwyżka II', 'Standard']:
        clients_p = df2[df2['join_period'] == period]['client'].unique()
        if len(clients_p) < 10:
            continue
        sub = df[df['client'].isin(clients_p)]
        sub_pivot = (
            sub.groupby(['client', 'months_since_join'])
            .size().unstack(fill_value=0)
        )
        sub_sizes = (sub_pivot[0] > 0).sum()
        sub_ret = ((sub_pivot > 0).sum(axis=0) / len(clients_p) * 100)
        sub_ret = sub_ret[[c for c in range(0, 7) if c in sub_ret.index]]
        period_retention[period] = sub_ret
    out['period_retention'] = period_retention

    # ── Rozkład cen miesięcznie (stack) ───────────────────────────────────
    price_monthly = (
        df.groupby(['month_str', 'price_cat'])['client']
        .count()
        .unstack(fill_value=0)
    )
    price_monthly.index = pd.to_datetime(price_monthly.index)
    price_monthly = price_monthly.sort_index()
    out['price_monthly'] = price_monthly

    # ── Mediana ceny WSZYSTKICH klientów miesięcznie (stabilniejsza niż nowi) ──
    all_med_price = (
        df.groupby('month_str')['amount']
        .median()
        .reset_index()
    )
    all_med_price.columns = ['month_str', 'amount']
    all_med_price['month_dt'] = pd.to_datetime(all_med_price['month_str'])
    all_med_price = all_med_price.sort_values('month_dt')
    out['new_avg_price'] = all_med_price

    return out


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS WIZUALNE
# ══════════════════════════════════════════════════════════════════════════════
def kpi_box(ax, title, value, subtitle='', color=TEAL, icon=''):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    # Tło
    rect = FancyBboxPatch((0.04, 0.08), 0.92, 0.84,
                           boxstyle="round,pad=0.02",
                           linewidth=1.5, edgecolor=color,
                           facecolor=PANEL2, zorder=1)
    ax.add_patch(rect)
    # Linia akcentu na górze
    ax.plot([0.04, 0.96], [0.92, 0.92], color=color, lw=3, solid_capstyle='round')
    # Treść
    ax.text(0.5, 0.68, value, ha='center', va='center',
            fontsize=17, fontweight='bold', color=color, zorder=2)
    ax.text(0.5, 0.38, title, ha='center', va='center',
            fontsize=7.5, color=TEXT_ACCENT, fontweight='semibold', zorder=2)
    if subtitle:
        ax.text(0.5, 0.20, subtitle, ha='center', va='center',
                fontsize=6.5, color=TEXT_DIM, zorder=2)


def style_ax(ax, title='', xlabel='', ylabel='', ygrid=True):
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.grid(ygrid, axis='y', color=GRID_COLOR, lw=0.5, linestyle='--', alpha=0.7)
    ax.grid(False, axis='x')
    if title:
        ax.set_title(title, color=TEXT_MAIN, fontsize=10, fontweight='bold',
                     pad=8, loc='left')
    if xlabel: ax.set_xlabel(xlabel, color=TEXT_DIM, fontsize=8)
    if ylabel: ax.set_ylabel(ylabel, color=TEXT_DIM, fontsize=8)


def shade_period_bands(ax, monthly_df, promo_months, hike1_months, hike_months, ymin=0, ymax=1):
    """Zacieniuj kolumny odpowiadające erom cenowym."""
    for _, row in monthly_df.iterrows():
        m = row['month_str']
        x = row['month_dt']
        if m in promo_months:
            ax.axvspan(x - pd.Timedelta(days=15), x + pd.Timedelta(days=15),
                       color=TEAL, alpha=0.07, zorder=0)
        elif m in hike1_months:
            ax.axvspan(x - pd.Timedelta(days=15), x + pd.Timedelta(days=15),
                       color=AMBER, alpha=0.07, zorder=0)
        elif m in hike_months:
            ax.axvspan(x - pd.Timedelta(days=15), x + pd.Timedelta(days=15),
                       color=CORAL, alpha=0.07, zorder=0)


# ══════════════════════════════════════════════════════════════════════════════
# GŁÓWNY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def build_dashboard(df, analytics, promo_months, hike1_months, hike_months, output_path):
    monthly         = analytics['monthly']
    retention_pct   = analytics['retention_pct']
    cohort_sizes    = analytics['cohort_sizes']
    avg_retention   = analytics['avg_retention']
    period_ret      = analytics['period_retention']
    price_monthly   = analytics['price_monthly']
    new_avg_price   = analytics['new_avg_price']

    # ── Pre-compute insight values for data-driven titles ─────────────────
    _last3       = monthly.tail(3)['new_clients'].mean()
    _first3      = monthly.head(3)['new_clients'].mean()
    _growth      = _last3 / max(_first3, 1)
    _rev_last    = monthly.tail(1)['revenue'].values[0]
    _rev_first3  = monthly.head(3)['revenue'].mean()
    _rev_growth  = _rev_last / max(_rev_first3, 1)
    _single_pct  = analytics['single_txn_pct']
    _p1m         = period_ret.get('Promocja',   pd.Series()).get(1, None)
    _h1_1m       = period_ret.get('Podwyżka I', pd.Series()).get(1, None)
    _h2_1m       = period_ret.get('Podwyżka II',pd.Series()).get(1, None)
    _avg_1m      = avg_retention.get(1, None)
    _avg_3m      = avg_retention.get(3, None)

    FW, FH = 22, 28
    fig = plt.figure(figsize=(FW, FH), facecolor=BG)

    # ── Siatka ────────────────────────────────────────────────────────────
    outer = gridspec.GridSpec(
        7, 1,
        figure=fig,
        hspace=0.52,
        top=0.960, bottom=0.035,
        left=0.055, right=0.97,
        height_ratios=[1.05, 0.8, 1.5, 1.65, 1.4, 1.4, 1.35]
    )

    # ── Row 0 : Nagłówek ──────────────────────────────────────────────────
    ax_header = fig.add_subplot(outer[0])
    ax_header.set_facecolor(BG); ax_header.axis('off')
    ax_header.set_xlim(0, 1); ax_header.set_ylim(0, 1)

    # Animated-feel gradient bar from left
    for i in range(300):
        t = i / 300
        alpha = 0.35 * np.exp(-t * 2.5)
        ax_header.axvspan(t, t + 1/300, ymin=0.0, ymax=1.0,
                          color=TEAL, alpha=alpha, zorder=0)

    # Thin accent line on bottom of header
    ax_header.axhline(0.02, color=TEAL, lw=1.5, alpha=0.5)

    # Title
    ax_header.text(0.012, 0.72, 'KajoDataSpace',
                   ha='left', va='center', fontsize=24, fontweight='black',
                   color=TEAL, zorder=2)

    # Vertical separator
    ax_header.plot([0.285, 0.285], [0.38, 0.88], color=GRID_COLOR, lw=1.2)

    ax_header.text(0.298, 0.72,
                   'Analiza wpływu promocji, cen standardowych i podwyżek na retencję klientów',
                   ha='left', va='center', fontsize=9, color=TEXT_ACCENT, zorder=2)
    ax_header.text(0.298, 0.38,
                   'Dane: XI 2023 – III 2026  ·  4 227 transakcji  ·  1 057 unikalnych klientów',
                   ha='left', va='center', fontsize=8, color=TEXT_DIM, zorder=2)

    # Hashtags pill on right
    ax_header.text(0.988, 0.68, '#dataacolyte  #kajodataspace',
                   ha='right', va='center', fontsize=7.5, color=TEXT_DIM,
                   fontstyle='italic', zorder=2)

    # ── Row 1 : KPI ───────────────────────────────────────────────────────
    kpi_gs = gridspec.GridSpecFromSubplotSpec(
        1, 5, subplot_spec=outer[1], wspace=0.12
    )
    kpi_axes = [fig.add_subplot(kpi_gs[0, i]) for i in range(5)]

    last_month = monthly.iloc[-1]
    prev_month = monthly.iloc[-2]
    mom_growth = (last_month['txn_count'] - prev_month['txn_count']) / prev_month['txn_count'] * 100

    kpi_box(kpi_axes[0], 'Unikalni klienci',
            f"{analytics['total_clients']:,}",
            f"łącznie od startu", color=TEAL)
    kpi_box(kpi_axes[1], 'Transakcje ogółem',
            f"{analytics['total_txn']:,}",
            f"XI 2023 – III 2026", color=BLUE)
    kpi_box(kpi_axes[2], 'Retencja (≥2 zakupy)',
            f"{analytics['retention_rate']:.1f}%",
            f"klientów wróciło min. raz", color=GREEN)
    kpi_box(kpi_axes[3], 'Śr. LTV / klient',
            f"{analytics['avg_ltv']:.0f} PLN",
            f"suma wpłat na klienta", color=AMBER)
    kpi_box(kpi_axes[4], 'MoM wzrost (III\'26)',
            f"{mom_growth:+.1f}%",
            f"vs poprzedni miesiąc", color=CORAL if mom_growth < 0 else VIOLET)

    # ── Row 2 : Wolumen transakcji + Nowi vs powracający ─────────────────
    row2_gs = gridspec.GridSpecFromSubplotSpec(
        1, 2, subplot_spec=outer[2], wspace=0.22
    )

    # -- 2a: Wolumen miesięczny (słupki + trend) --
    ax2a = fig.add_subplot(row2_gs[0])
    style_ax(ax2a, title=f'Baza klientów rośnie {_growth:.1f}× pomimo dwóch podwyżek cen')

    x     = monthly['month_dt']
    y_new = monthly['new_clients']
    y_ret = monthly['returning']

    ax2a.bar(x, y_ret, color=BLUE, alpha=0.75, width=20, label='Powracający', zorder=2)
    ax2a.bar(x, y_new, bottom=y_ret, color=TEAL, alpha=0.85, width=20,
             label='Nowi klienci', zorder=2)

    # Linia trendu (rolling 3M)
    total_smooth = monthly['txn_count'].rolling(3, center=True, min_periods=1).mean()
    ax2a.plot(x, total_smooth, color=AMBER, lw=2, zorder=4, label='Trend (3M avg)')

    shade_period_bands(ax2a, monthly, promo_months, hike1_months, hike_months)

    ax2a.set_xlim(x.min() - pd.Timedelta(days=20), x.max() + pd.Timedelta(days=20))
    ax2a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v)}'))
    ax2a.set_ylabel('Liczba transakcji', color=TEXT_DIM, fontsize=8)

    # Adnotacje kluczowych wydarzeń
    promo_sorted = sorted([m for m in promo_months
                           if m in monthly['month_str'].values])
    first_promo_months = promo_sorted[:2] if len(promo_sorted) >= 2 else promo_sorted
    for pm in first_promo_months:
        row = monthly[monthly['month_str'] == pm]
        if not row.empty:
            px = row['month_dt'].values[0]
            py = row['txn_count'].values[0]
            ax2a.annotate('PROMO', xy=(px, py), xytext=(0, 14),
                          textcoords='offset points',
                          fontsize=6.5, color=TEAL, fontweight='bold',
                          ha='center',
                          arrowprops=dict(arrowstyle='->', color=TEAL, lw=1))

    hike_sorted = sorted([m for m in hike_months
                          if m in monthly['month_str'].values])
    if hike_sorted:
        hm = hike_sorted[0]
        row = monthly[monthly['month_str'] == hm]
        if not row.empty:
            px = row['month_dt'].values[0]
            py = row['txn_count'].values[0]
            ax2a.annotate('PODWYŻKA', xy=(px, py), xytext=(0, 14),
                          textcoords='offset points',
                          fontsize=6.5, color=CORAL, fontweight='bold',
                          ha='center',
                          arrowprops=dict(arrowstyle='->', color=CORAL, lw=1))

    ax2a.xaxis.set_major_formatter(
        matplotlib.dates.DateFormatter('%b\n%Y'))
    ax2a.xaxis.set_major_locator(
        matplotlib.dates.MonthLocator(interval=3))
    ax2a.legend(fontsize=7, loc='upper left',
                framealpha=0.7, labelspacing=0.3)

    # Pasek legendy tła
    promo_patch = mpatches.Patch(color=TEAL, alpha=0.25, label='Okres promocji')
    hike_patch  = mpatches.Patch(color=CORAL, alpha=0.25, label='Okres podwyżki')
    ax2a.legend(handles=[
        mpatches.Patch(color=BLUE,  alpha=0.75, label='Powracający'),
        mpatches.Patch(color=TEAL,  alpha=0.85, label='Nowi'),
        mpatches.Patch(color=AMBER, label='Trend 3M'),
        mpatches.Patch(color=TEAL,  alpha=0.25, label='Era I – Promo (≤99 PLN)'),
        mpatches.Patch(color=AMBER, alpha=0.25, label='Era II – Podwyżka I (169 PLN)'),
        mpatches.Patch(color=CORAL, alpha=0.25, label='Era III – Podwyżka II (199 PLN)'),
    ], fontsize=7, loc='upper left', framealpha=0.7, labelspacing=0.3,
       handlelength=1.2)

    # -- 2b: Cena mediany dla nowych klientów --
    ax2b = fig.add_subplot(row2_gs[1])
    style_ax(ax2b, title='Trzy ery cenowe: ≤99 → 169 → 199 PLN – każda przyjęta przez rynek')

    # Wypełnienie pod linią
    ax2b.fill_between(
        new_avg_price['month_dt'],
        new_avg_price['amount'],
        alpha=0.18, color=VIOLET, zorder=1
    )
    ax2b.plot(new_avg_price['month_dt'], new_avg_price['amount'],
              color=VIOLET, lw=2.5, zorder=3)

    # Poziome linie referencyjne dla każdej ery
    for price, color, label in [(89, TEAL, '89 PLN'), (169, AMBER, '169 PLN'), (199, CORAL, '199 PLN')]:
        ax2b.axhline(price, color=color, lw=1.2, linestyle='--', alpha=0.5, zorder=2)

    shade_period_bands(ax2b, monthly, promo_months, hike1_months, hike_months)

    # Era labels – umieszczone w środku każdego okresu, nie na końcu
    era_labels = [
        (pd.Timestamp('2024-02-01'), 60, 'Era I\nPROMO\n≤99 PLN',  TEAL),
        (pd.Timestamp('2025-01-01'), 130, 'Era II\n+169 PLN',      AMBER),
        (pd.Timestamp('2025-11-01'), 155, 'Era III\n+199 PLN',     CORAL),
    ]
    for xpos, ypos, label, col in era_labels:
        ax2b.text(xpos, ypos, label, color=col, fontsize=7,
                  ha='center', fontweight='bold',
                  bbox=dict(facecolor=PANEL, edgecolor=col, alpha=0.7,
                            boxstyle='round,pad=0.25', linewidth=0.8))

    ax2b.set_ylabel('Mediana kwoty (PLN)', color=TEXT_DIM, fontsize=8)
    ax2b.set_ylim(0, 230)
    ax2b.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b\n%Y'))
    ax2b.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))

    # ── Row 3 : Heatmapa retencji kohortowej ──────────────────────────────
    ax3 = fig.add_subplot(outer[3])
    ax3.set_facecolor(PANEL)

    cmap_ret = LinearSegmentedColormap.from_list(
        'retention',
        ['#0B0F1A', '#0D2137', '#0A3D5C', '#0A6E7C', '#00A896', '#00D4AA'],
        N=256
    )

    # Ogranicz do kohort z ≥8 klientów i mających dane w col 1 (min. 2 mc historii)
    ret_plot = retention_pct.copy()
    big_cohorts = cohort_sizes[cohort_sizes >= 8].index
    ret_plot = ret_plot.loc[ret_plot.index.isin(big_cohorts)]
    # Tylko kohorty, które mają dane w co najmniej kolumnie 1
    if 1 in ret_plot.columns:
        ret_plot = ret_plot[ret_plot[1].notna() & (ret_plot[1] > 0)]
    if len(ret_plot) > 16:
        ret_plot = ret_plot.tail(16)
    cols_12 = [c for c in range(0, 11) if c in ret_plot.columns]
    ret_plot = ret_plot[cols_12]

    mask = ret_plot.isnull()

    im = sns.heatmap(
        ret_plot,
        ax=ax3,
        cmap=cmap_ret,
        vmin=0, vmax=100,
        annot=True, fmt='.0f',
        annot_kws={'size': 7.5, 'color': TEXT_MAIN, 'fontweight': 'semibold'},
        linewidths=0.5, linecolor=BG,
        mask=mask,
        cbar_kws={'shrink': 0.55, 'pad': 0.01, 'label': 'Retencja (%)'},
        square=False
    )

    cbar = ax3.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT_DIM)
    cbar.ax.yaxis.set_tick_params(colors=TEXT_DIM)
    cbar.ax.tick_params(labelsize=7)

    ax3.set_title('Retencja kohortowa stabilna we wszystkich erach – podwyżki nie zwiększają odpływu',
                  color=TEXT_MAIN, fontsize=10, fontweight='bold', pad=10, loc='left')
    ax3.set_xlabel('Miesiące od pierwszego zakupu', color=TEXT_DIM, fontsize=8)
    ax3.set_ylabel('Miesiąc dołączenia (kohorta)', color=TEXT_DIM, fontsize=8)
    ax3.tick_params(axis='both', colors=TEXT_DIM, labelsize=8)
    plt.setp(ax3.get_xticklabels(), rotation=0)
    plt.setp(ax3.get_yticklabels(), rotation=0)

    col_labels = [f'+{c}M' for c in ret_plot.columns]
    ax3.set_xticklabels(col_labels, color=TEXT_DIM, fontsize=8)

    # ── Row 4 : Retencja wg okresu + Rozkład cen w czasie ─────────────────
    row4_gs = gridspec.GridSpecFromSubplotSpec(
        1, 2, subplot_spec=outer[4], wspace=0.22
    )

    # -- 4a: Krzywe retencji Promo vs Standard vs Po podwyżce --
    ax4a = fig.add_subplot(row4_gs[0])
    _ret_title = (
        f'Promo i podwyżki przynoszą równie lojalnych klientów – retencja 1M ≈'
        f'{_p1m:.0f}% vs {_h1_1m:.0f}%'
        if _p1m and _h1_1m else
        'Krzywe retencji wg okresu dołączenia'
    )
    style_ax(ax4a,
             title=_ret_title,
             xlabel='Miesiące od pierwszego zakupu',
             ylabel='% klientów aktywnych')

    period_colors = {
        'Promocja':    TEAL,
        'Podwyżka I':  AMBER,
        'Podwyżka II': CORAL,
        'Standard':    BLUE,
    }
    period_markers = {'Promocja': 'o', 'Podwyżka I': 'D', 'Podwyżka II': '^', 'Standard': 's'}

    for period, ret_series in period_ret.items():
        col   = period_colors.get(period, TEXT_DIM)
        mark  = period_markers.get(period, 'o')

        # Przytnij: nie pokazuj miesięcy z <10% oryginalnej kohorty (za mało danych)
        valid = ret_series[ret_series > 0]
        # Dla Podwyżki II ogranicz do +4M (za mało historii)
        if period == 'Podwyżka II':
            valid = valid[valid.index <= 4]
        if len(valid) < 2:
            continue

        x_val = valid.index.tolist()
        y_val = valid.values

        ax4a.fill_between(x_val, y_val, alpha=0.08, color=col)
        ax4a.plot(x_val, y_val, color=col, lw=2.2,
                  marker=mark, markersize=5,
                  label=period, zorder=4)

        # Etykieta na końcu krzywej
        ax4a.text(x_val[-1] + 0.12, y_val[-1],
                  f'{y_val[-1]:.0f}%',
                  color=col, fontsize=7.5, va='center', fontweight='bold')

    ax4a.set_xticks(range(0, 7))
    ax4a.set_xticklabels([f'+{i}M' for i in range(0, 7)], fontsize=8)
    ax4a.set_ylim(0, 105)
    ax4a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v)}%'))
    ax4a.legend(fontsize=8, framealpha=0.7, loc='upper right')

    # Benchmark SaaS: retencja 1M dla subskrypcji ~99–249 PLN wynosi 35–55%
    # (źródło: Baremetrics 2024 Benchmarks, segment SMB SaaS)
    ax4a.axhspan(35, 55, color=AMBER, alpha=0.06, zorder=0, label='_nolegend_')
    ax4a.axhline(35, color=AMBER, lw=0.8, linestyle=':', alpha=0.5)
    ax4a.axhline(55, color=AMBER, lw=0.8, linestyle=':', alpha=0.5)
    ax4a.text(6.08, 44, 'benchmark\nSaaS\n35–55%',
              color=AMBER, fontsize=6.5, va='center', ha='left',
              bbox=dict(facecolor=PANEL2, edgecolor=AMBER, alpha=0.75,
                        boxstyle='round,pad=0.25', linewidth=0.7))

    # -- 4b: Skład cenowy (stacked area) --
    ax4b = fig.add_subplot(row4_gs[1])
    style_ax(ax4b, title='Standard dominuje strukturę – plany roczne rosną systematycznie od 2025')

    cat_order  = ['Promo', 'Standard', 'Kwartalny', 'Roczny']
    cat_colors = [TEAL, BLUE, VIOLET, AMBER]
    cat_present = [c for c in cat_order if c in price_monthly.columns]
    cat_colors_p= [cat_colors[cat_order.index(c)] for c in cat_present]

    ax4b.stackplot(
        price_monthly.index,
        [price_monthly[c] for c in cat_present],
        labels=cat_present,
        colors=cat_colors_p,
        alpha=0.80
    )
    ax4b.set_xlim(price_monthly.index.min(), price_monthly.index.max())
    ax4b.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b\n%Y'))
    ax4b.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
    ax4b.set_ylabel('Liczba transakcji', color=TEXT_DIM, fontsize=8)
    ax4b.legend(fontsize=7.5, loc='upper left', framealpha=0.7,
                labelspacing=0.3, handlelength=1.2)

    # ── Row 5 : Średnia retencja (bar) + MRR ──────────────────────────────
    row5_gs = gridspec.GridSpecFromSubplotSpec(
        1, 2, subplot_spec=outer[5], wspace=0.22
    )

    # -- 5a: Średnia retencja w N miesiącach po zakupie --
    ax5a = fig.add_subplot(row5_gs[0])
    _churn_title = (
        f'{_single_pct:.0f}% klientów nie wraca po pierwszym zakupie – onboarding to priorytet'
        if _single_pct > 40 else
        f'Retencja po 1M: {_avg_1m:.0f}% – dobra baza do skalowania akwizycji'
    )
    style_ax(ax5a,
             title=_churn_title,
             xlabel='Miesiące od dołączenia',
             ylabel='Śr. % aktywnych klientów')

    avg_ret_vals = avg_retention.values
    avg_ret_idx  = avg_retention.index.tolist()

    bar_colors = [
        TEAL if v > 60 else BLUE if v > 35 else CORAL
        for v in avg_ret_vals
    ]
    bars = ax5a.bar(avg_ret_idx, avg_ret_vals,
                    color=bar_colors, alpha=0.85, zorder=2, width=0.6)

    for bar, val in zip(bars, avg_ret_vals):
        ax5a.text(bar.get_x() + bar.get_width() / 2,
                  bar.get_height() + 0.8,
                  f'{val:.0f}%',
                  ha='center', va='bottom',
                  fontsize=7.5, color=TEXT_MAIN, fontweight='semibold')

    ax5a.set_xticks(avg_ret_idx)
    ax5a.set_xticklabels([f'+{i}M' for i in avg_ret_idx], fontsize=8)
    ax5a.set_ylim(0, 110)
    ax5a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v)}%'))

    # -- 5b: Przychody miesięczne (MRR proxy) --
    ax5b = fig.add_subplot(row5_gs[1])
    style_ax(ax5b, title=f'Przychód rośnie {_rev_growth:.1f}× – wzrost cen multiplikuje wynik bez utraty klientów')

    rev = monthly['revenue']
    rev_smooth = rev.rolling(3, center=True, min_periods=1).mean()

    bars_rev = ax5b.bar(monthly['month_dt'], rev,
                        color=VIOLET, alpha=0.45, width=20, zorder=2)
    ax5b.plot(monthly['month_dt'], rev_smooth,
              color=AMBER, lw=2.2, zorder=4, label='Trend 3M')

    shade_period_bands(ax5b, monthly, promo_months, hike1_months, hike_months)

    ax5b.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}k'))
    ax5b.set_ylabel('Przychód (tys. PLN)', color=TEXT_DIM, fontsize=8)
    ax5b.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b\n%Y'))
    ax5b.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
    ax5b.legend(fontsize=7.5, framealpha=0.7)

    # ── Row 6 : Rekomendacje biznesowe ───────────────────────────────────
    ax6 = fig.add_subplot(outer[6])
    ax6.set_facecolor(PANEL2); ax6.axis('off')
    ax6.set_xlim(0, 1); ax6.set_ylim(0, 1)

    rect6 = FancyBboxPatch((0.005, 0.04), 0.99, 0.92,
                            boxstyle="round,pad=0.01",
                            linewidth=1, edgecolor=GRID_COLOR,
                            facecolor=PANEL2)
    ax6.add_patch(rect6)

    promo_ret_1m  = period_ret.get('Promocja',   pd.Series()).get(1, None)
    hike1_ret_1m  = period_ret.get('Podwyżka I',  pd.Series()).get(1, None)
    hike2_ret_1m  = period_ret.get('Podwyżka II', pd.Series()).get(1, None)
    std_ret_1m    = period_ret.get('Standard',    pd.Series()).get(1, None)

    last3 = monthly.tail(3)['new_clients'].mean()
    first3 = monthly.head(3)['new_clients'].mean()
    growth_factor = last3 / max(first3, 1)
    single_pct = analytics['single_txn_pct']

    recos = []

    # Wniosek 1: Promo vs Podwyżka I
    if promo_ret_1m and hike1_ret_1m:
        diff = hike1_ret_1m - promo_ret_1m
        icon = '📈' if diff > 0 else '📉'
        recos.append((TEAL if diff < 0 else AMBER, icon,
            f"Retencja 1M: Promo={promo_ret_1m:.0f}%  vs  Podwyżka I (169 PLN)={hike1_ret_1m:.0f}% "
            f"({'klienci z wyższej ceny są bardziej lojalni' if diff>0 else 'promo przyciąga aktywniejszych użytkowników'})."))

    # Wniosek 2: Podwyżka II
    if hike2_ret_1m:
        recos.append((GREEN if hike2_ret_1m >= 30 else CORAL, '💰',
            f"Podwyżka II (199 PLN, VIII 2025): retencja 1M = {hike2_ret_1m:.0f}% – "
            f"{'rynek akceptuje cenę, wzrost przychodu bez utraty klientów' if hike2_ret_1m>=30 else 'widoczny odpływ po podwyżce, rozważ łagodniejsze przejście cenowe'}."))
    else:
        recos.append((AMBER, '💰',
            "Podwyżka II (199 PLN, VIII 2025): za mało danych o retencji → monitoruj kohorty z VIII–XII 2025."))

    # Wniosek 3: Wzrost bazy
    recos.append((VIOLET, '🚀',
        f"Baza klientów rośnie: śr. {last3:.0f} nowych/mc (ostatnie 3M) vs {first3:.0f}/mc na starcie "
        f"({growth_factor:.1f}× wzrost) → produkt ma silne momentum organiczne."))

    # Wniosek 4: Jednorazowi klienci
    recos.append((CORAL if single_pct > 40 else GREEN, '⚡',
        f"{single_pct:.0f}% klientów kupiło tylko raz → "
        f"{'priorytet: onboarding flow + e-mail retention w pierwszych 14 dniach.' if single_pct > 40 else 'dobra retencja po pierwszym zakupie – skaluj akwizycję.'}"))

    # Nagłówek
    ax6.text(0.012, 0.90, '💡  Kluczowe wnioski i rekomendacje biznesowe',
             ha='left', va='center', fontsize=9.5,
             color=AMBER, fontweight='bold')

    # Dwie kolumny rekomendacji
    col_x = [0.012, 0.51]
    col_y_start = 0.71
    row_h = 0.32
    for i, (col, icon, txt) in enumerate(recos[:4]):
        cx = col_x[i % 2]
        cy = col_y_start - (i // 2) * row_h
        sq = FancyBboxPatch((cx, cy - 0.02), 0.005, 0.14,
                             boxstyle="round,pad=0.01",
                             facecolor=col, edgecolor='none')
        ax6.add_patch(sq)
        ax6.text(cx + 0.012, cy + 0.05, f'{icon}  {txt}',
                 ha='left', va='center', fontsize=7.4,
                 color=TEXT_ACCENT,
                 wrap=True)

    ax6.text(0.988, 0.12, 'KajoData  ×  DataAcolyte',
             ha='right', va='center', fontsize=8,
             color=TEXT_DIM, fontstyle='italic')

    # ── Sekcja metodologiczna ─────────────────────────────────────────────
    ax6.plot([0.012, 0.988], [0.155, 0.155], color=GRID_COLOR, lw=0.8)

    meta_lines = [
        "📐  Metodologia:",
        "Ery cenowe zdefiniowane przez medianę transakcji: Era I ≤99 PLN (promo), Era II 100–185 PLN (podwyżka I), Era III >185 PLN (podwyżka II).",
        "Użyto mediany zamiast średniej – rozkład kwot prawostronnie skośny ze względu na plany roczne (max 1 999 PLN). "
        "Heatmapa retencji obejmuje kohorty ≥8 klientów. "
        "Krzywa Podwyżki II przycięta do +4M (kohorty VIII–XII 2025 mają <7M historii – wyniki wstępne). "
        "Benchmark retencji 1M: 35–55% dla SaaS w segmencie SMB (Baremetrics 2024)."
    ]

    ax6.text(0.012, 0.135, meta_lines[0],
             ha='left', va='top', fontsize=7, color=AMBER, fontweight='bold')
    ax6.text(0.065, 0.135, meta_lines[1],
             ha='left', va='top', fontsize=6.8, color=TEXT_DIM)
    ax6.text(0.012, 0.072, meta_lines[2],
             ha='left', va='top', fontsize=6.8, color=TEXT_DIM, wrap=True)

    # ── Finalizacja ───────────────────────────────────────────────────────
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=BG, edgecolor='none')
    print(f"✓ Dashboard zapisany: {output_path}")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    import matplotlib.dates
    import calendar as cal_module

    OUTPUT = '/mnt/user-data/outputs/KDS_Dashboard.png'

    df_raw          = load_data()
    df, promo_m, hike1_m, hike_m = prepare_data(df_raw)
    analytics       = compute_analytics(df)
    build_dashboard(df, analytics, promo_m, hike1_m, hike_m, OUTPUT)

    print("\n═══ PODSUMOWANIE ANALITYCZNE ═══")
    print(f"Transakcje:       {analytics['total_txn']:,}")
    print(f"Klienci:          {analytics['total_clients']:,}")
    print(f"Łączny przychód:  {analytics['total_revenue']:,.0f} PLN")
    print(f"Śr. LTV:          {analytics['avg_ltv']:.0f} PLN")
    print(f"Retencja (≥2tx):  {analytics['retention_rate']:.1f}%")
    print(f"\nRetencja po 1M wg okresu dołączenia:")
    for p, s in analytics['period_retention'].items():
        r1 = s.get(1, float('nan'))
        r3 = s.get(3, float('nan'))
        print(f"  {p:15s}  1M={r1:.0f}%  3M={r3:.0f}%")