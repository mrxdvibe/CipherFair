import csv
import argparse
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

COST_PER_IMPACT_POINT = {
    1: 500, 2: 1500, 3: 5000, 4: 10000, 5: 25000,
    6: 50000, 7: 100000, 8: 250000, 9: 500000
}

SPECIALITY_MULTIPLIERS = {
    "oncology": 1.5,
    "cardiology": 1.4,
    "pediatric": 1.3,
    "emergency": 1.2,
    "radiology": 1.1
}

def get_multiplier(speciality):
    if not speciality:
        return 1.0
    spec_lower = speciality.lower()
    max_multiplier = 1.0
    for key, value in SPECIALITY_MULTIPLIERS.items():
        if key in spec_lower and value > max_multiplier:
            max_multiplier = value
    return max_multiplier

def analyze(csv_file, filter_score=None, show_all=False):
    total_loss = 0
    incidents = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) 
            
            for row in reader:
                if not row or len(row) < 9:
                    continue
                try:
                    impact_score = int(row[8])
                except ValueError:
                    continue
                
                if filter_score and impact_score < filter_score:
                    continue

                speciality = row[6].strip()
                multiplier = get_multiplier(speciality)
                
                base_loss = COST_PER_IMPACT_POINT.get(impact_score, 0)
                final_loss = base_loss * multiplier
                
                total_loss += final_loss
                incidents.append({
                    'score': impact_score, 
                    'loss': final_loss, 
                    'harm': row[3], 
                    'speciality': speciality
                })
    except FileNotFoundError:
        console.print(f"[bold red]Xəta:[/bold red] '{csv_file}' faylı tapılmadı!")
        return

    incidents.sort(key=lambda x: x['loss'], reverse=True)

    # Yuxarı Panel: Daha böyük, geniş və aydın
    console.print(Panel(
        f"[bold white]Analiz Edilən Hadisə:[/bold white] [bold cyan]{len(incidents)}[/bold cyan]\n"
        f"[bold white]Ümumi Təxmini İtki:[/bold white] [bold green]${total_loss:,.2f}[/bold green]", 
        title="[bold white]CIPHER-FAIR Maliyyə Hesabatı[/bold white]", 
        border_style="white", 
        expand=True, # Bu hissə paneli tam enə yayır
        padding=(1, 2) # Panelin daxili boşluğunu (hündürlüyünü) artırır
    ))
    console.print() 

    # Cədvəl: Bütün yazılar eyni rəngdə (ağ)
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold white")
    table.add_column("Risk", justify="center", style="white")
    table.add_column("Tibb Sahəsi", style="white")
    table.add_column("Maliyyə İtkisi", justify="right", style="green")
    table.add_column("Hadisənin Təsviri", style="white", max_width=60)

    limit = len(incidents) if show_all else 10
    for inc in incidents[:limit]:
        score_text = f"[bold red]{inc['score']}/9[/bold red]" if inc['score'] >= 8 else f"{inc['score']}/9"
        
        table.add_row(
            score_text,
            inc['speciality'][:22] + ("..." if len(inc['speciality']) > 22 else ""),
            f"${inc['loss']:,.2f}",
            inc['harm']
        )
    
    console.print(table)
    console.print() 

    # Qrafik hissəsi eyni qalır
    if incidents:
        top_5 = incidents[:5]
        labels = [f"{inc['speciality']}\n(Score: {inc['score']})" for inc in top_5]
        costs = [inc['loss'] for inc in top_5]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(labels, costs, color=['#8b0000', '#b22222', '#dc143c', '#cd5c5c', '#f08080'])
        
        plt.title('Top 5 Kiber-Klinik Hadisənin Maliyyə İtkisi', fontsize=14)
        plt.ylabel('Maliyyə İtkisi ($)', fontsize=12)
        plt.xlabel('Tibb Sahəsi və Risk Balı', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 10000, f'${yval:,.0f}', 
                     ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig('risk_report.png')
        console.print("[green]Qrafik 'risk_report.png' faylına yadda saxlanıldı.[/green]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kiber-Klinik Maliyyə Tərcümə Aləti")
    parser.add_argument("file", help="CSV faylının adı")
    parser.add_argument("--min-score", type=int, help="Yalnız müəyyən baldan yuxarı olanları göstər")
    parser.add_argument("--all", action="store_true", help="Bütün hadisələri göstər")
    
    args = parser.parse_args()
    analyze(args.file, args.min_score, args.all)
