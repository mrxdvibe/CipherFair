import csv

# FAIR Modelinə əsasən Klinik Zərərin Maliyyə Yükü
COST_PER_IMPACT_POINT = {
    1: 500, 2: 1500, 3: 5000, 4: 10000, 5: 25000,
    6: 50000, 7: 100000, 8: 250000, 9: 500000
}

def analyze_risk(csv_file):
    print(f"--- REAL MALİYYƏ ANALİZİ BAŞLAYIR ---\n")
    total_loss = 0
    incidents = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Başlığı keç
        
        for row in reader:
            if not row or len(row) < 9:
                continue
            
            harm_desc = row[3]
            try:
                impact_score = int(row[8])
            except ValueError:
                continue 

            estimated_loss = COST_PER_IMPACT_POINT.get(impact_score, 0)
            total_loss += estimated_loss
            
            incidents.append({
                'harm': harm_desc,
                'score': impact_score,
                'loss': estimated_loss
            })

    # Ən bahalı hadisələri sıralayaq
    incidents.sort(key=lambda x: x['loss'], reverse=True)
    
    print(f"Ümumi hadisə sayı: {len(incidents)}")
    print(f"Təxmini Ümumi Maliyyə İtkisi (ALE): ${total_loss:,.2f}\n")
    
    print("--- ƏN YÜKSƏK MALİYYƏ RİSKLİ HADİSƏLƏR ---")
    for inc in incidents[:5]:
        print(f"[{inc['score']} BAL] ${inc['loss']:,.2f} -> {inc['harm'][:80]}...")

if __name__ == "__main__":
    analyze_risk('v1_cipherdata_latest.csv')
