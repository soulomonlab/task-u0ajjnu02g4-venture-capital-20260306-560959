"""
Data generator for Venture Capital ML feasibility sample.
Generates:
 - data/venture_capital_10k_sample.csv (10,000 rows)
 - data/user_interactions_sample.csv (optional interactions)

Run from project root with working_dir=output/ as:
  python output/code/data/generate_vc_sample.py

This script uses only Python stdlib.
"""
import csv
import os
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_DIR = 'data'
VC_FILENAME = 'venture_capital_10k_sample.csv'
INTERACTIONS_FILENAME = 'user_interactions_sample.csv'
NUM_ROWS = 10000
NUM_INTERACTIONS = 30000

os.makedirs(OUTPUT_DIR, exist_ok=True)

SECTORS = ['fintech','healthcare','ai','saas','marketplace','ecommerce','biotech','cleantech','crypto','edtech']
STAGES = ['pre_seed','seed','series_a','series_b','series_c','series_d','private_equity']
EVENT_TYPES = ['view','save','click']

LOREM = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut "
         "labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris")
WORDS = LOREM.split()

INVESTOR_POOL = [f"inv_{i:05d}" for i in range(1,501)]  # 500 synthetic investor ids

def rand_sentence(min_words=8, max_words=24):
    return ' '.join(random.choices(WORDS, k=random.randint(min_words, max_words))).capitalize() + '.'

def rand_company():
    prefixes = ['Nova','Pioneer','Summit','Blue','Green','Red','Nimbus','Vertex','Quantum','Apex','Halo']
    suffixes = ['Labs','Systems','Technologies','Works','Health','Capital','Analytics','Logix','Solutions','Dynamics']
    return random.choice(prefixes) + ' ' + random.choice(suffixes)

def rand_title():
    adjectives = ['Smart','Open','Easy','Connected','Cloud','Market','Deep','Mobile','Secure','NextGen']
    nouns = ['Payments','Platform','AI','Insights','Retail','Care','Fabric','Engine','Network','Optimizer']
    return random.choice(adjectives) + ' ' + random.choice(nouns)

def rand_date(start_year=2010, end_year=2023):
    start = datetime(start_year,1,1)
    end = datetime(end_year,12,31)
    delta = end - start
    d = start + timedelta(days=random.randint(0, delta.days))
    return d.date().isoformat()

# Generate VC deals CSV
vc_path = os.path.join(OUTPUT_DIR, VC_FILENAME)
with open(vc_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    header = ['deal_id','title','description','company_name','sector_tags','funding_stage','amount_usd','round_date','lead_investor_ids','outcome_label','created_at','updated_at']
    writer.writerow(header)

    for i in range(NUM_ROWS):
        deal_id = str(uuid.uuid4())
        title = rand_title()
        description = rand_sentence(12,40)
        company_name = rand_company()
        sectors = ';'.join(random.sample(SECTORS, k=random.randint(1,3)))
        stage = random.choices(STAGES, weights=[5,20,25,20,12,10,8], k=1)[0]
        amount = random.randint(25000, 200_000_000)
        round_date = rand_date()
        num_leads = random.choices([0,1,2,3], weights=[10,60,20,10], k=1)[0]
        leads = ';'.join(random.sample(INVESTOR_POOL, k=num_leads)) if num_leads>0 else ''
        # outcome_label available ~30% of rows
        if random.random() < 0.30:
            outcome = random.choices(['0','1'], weights=[60,40], k=1)[0]
        else:
            outcome = ''
        created_at = datetime.utcnow().isoformat()
        # updated_at may be after created_at by up to 365 days
        updated_at = (datetime.utcnow() + timedelta(days=random.randint(0,365))).isoformat()

        row = [deal_id, title, description, company_name, sectors, stage, amount, round_date, leads, outcome, created_at, updated_at]
        writer.writerow(row)

# Generate optional user interactions
interactions_path = os.path.join(OUTPUT_DIR, INTERACTIONS_FILENAME)
deal_ids = []
# collect some deal_ids from generated file by reading first few lines to index deals
with open(vc_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for idx, r in enumerate(reader):
        deal_ids.append(r['deal_id'])
        if idx >= NUM_ROWS-1:
            break

user_pool = [f'user_{i:07d}' for i in range(1,5001)]  # 5k synthetic users

with open(interactions_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id','deal_id','event_type','timestamp'])
    for i in range(NUM_INTERACTIONS):
        user_id = random.choice(user_pool)
        deal_id = random.choice(deal_ids)
        event = random.choice(EVENT_TYPES)
        ts = (datetime.utcnow() - timedelta(days=random.randint(0,1000), seconds=random.randint(0,86400))).isoformat()
        writer.writerow([user_id, deal_id, event, ts])

print(f"Wrote VC sample: {vc_path} ({NUM_ROWS} rows)")
print(f"Wrote interactions: {interactions_path} ({NUM_INTERACTIONS} rows)")
