import random
import requests
from django.shortcuts import render, redirect
from .forms import FiveSummonerForm

# トロールネタ:レアリティで定義
TROLLS = [
    ("ワードを一切置かない。", "コモン"),
    ("常にミッドレーンに集合する。", "コモン"),
    ("ブーツを売って裸足で戦う。", "アンコモン"),
    ("買い物はサポートアイテムのみ。", "アンコモン"),
    ("ドラゴン・バロンは絶対触らない。", "レア"),
    ("リコール禁止。", "レア"),
    ("ジャングルにしか現れない。", "スーパーレア"),
    ("常に敵ジャングルでファームする。", "スーパーレア"),
    ("絶対にサモナースペルを使わない。", "ウルトラレア"),
    ("全アイテムを涙だけで揃える。", "ウルトラレア"),
]

# レアリティごとの排出率 (合計100)
RARITY_WEIGHTS = {
    "コモン": 50,
    "アンコモン": 25,
    "レア": 15,
    "スーパーレア": 7,
    "ウルトラレア": 3,
}

#チャンピオン専用トロール内容
SPECIAL_TROLLS = {
    "サイオン":"パッシブを有効活用する事を言い訳に、試合終了までに10デス以上行う",
    "ノーチラス":"ルーンを覇道、ビルドをフルapにする",
    "オラフ":" ",
    "ドレイヴン":" ",
    "カシオペア":" ",
    "ブリッツクランク":" ",
}

ROLES = ['TOP', 'JG', 'MID', 'ADC', 'SUP']


def get_latest_version():
    """Data Dragonの最新バージョンを取得（失敗時は固定値フォールバック）"""
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/api/versions.json", timeout=5)
        r.raise_for_status()
        return r.json()[0]
    except Exception:
        return "14.17.1"  # 失敗時の保険

def get_champion_data_ja(version):
    """日本語のチャンピオン一覧を取得（id=英語キー, name=日本語名）"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ja_JP/champion.json"
    r = requests.get(url, timeout=6)
    r.raise_for_status()
    return r.json()["data"]  # 例: {"Aatrox": {"id":"Aatrox","name":"エイトロックス",...}, ...}

def index(request):
    if request.method == "POST":
        summoners = [request.POST.get(f"summoner{i}") for i in range(1, 6)]
        troll_count = int(request.POST.get("troll_count", 1))
        request.session["troll_count"] = troll_count
        form = FiveSummonerForm(request.POST)
        if form.is_valid():
            summoners = [form.cleaned_data[f"summoner{i}"] for i in range(1, 6)]
            exclude_yuumi = form.cleaned_data["exclude_yuumi"]
            request.session["summoners"] = summoners
            request.session["exclude_yuumi"] = exclude_yuumi #ユーミの除外をセッションに保存
            return redirect("gacha:result")
    else:
        form = FiveSummonerForm()
    return render(request, "gacha/index.html", {"form": form})

def get_random_troll():
    #レアリティ抽選
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    # 選ばれたレアリティから内容をランダムに選ぶ
    candidates = [t for t in TROLLS if t[1] == chosen_rarity]
    content, rarity = random.choice(candidates)
    return content, rarity

def result(request):
    summoners = request.session.get("summoners")
    exclude_yuumi = request.session.get("exclude_yuumi", False)
    troll_count = int(request.session.get("troll_count", 1))  # ← 縛り人数を取得

    if not summoners or len(summoners) != 5:
        return redirect("gacha:index")

    # 最新データ
    version = get_latest_version()
    champ_data = get_champion_data_ja(version)  # dict: key=英語ID, valueに日本語名など
    
    if exclude_yuumi:
        champ_data = {cid: data for cid, data in champ_data.items() if data["name"] != "ユーミ"}

    champ_ids = list(champ_data.keys())

    # サモナーをシャッフル
    shuffled_summoners = random.sample(summoners, k=5)

    # チャンピオンを重複なしで選ぶ
    chosen_champ_ids = random.sample(champ_ids, k=5)

    # --- 縛りを付与する対象をランダムで選ぶ ---
    troll_indices = set(random.sample(range(5), k=troll_count))

    #トロール候補をユニークに確保するし、TROLLSをシャッフルする
    troll_pool = TROLLS[:]
    random.shuffle(troll_pool)

    results = []
    for i, role in enumerate(ROLES):  # ROLESは固定 ["TOP", "JG", "MID", "ADC", "SUP"]
        champ_id = chosen_champ_ids[i]
        champ_jp = champ_data[champ_id]["name"]
        img_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champ_id}.png"
        
        if i in troll_indices:
            # --- トロール抽選 ---
            if champ_jp in SPECIAL_TROLLS:
                troll_content = SPECIAL_TROLLS[champ_jp]
                rarity = "スペシャル"
            else:
                #プールから1つ消費
                troll_content, rarity = troll_pool.pop()
        else:
            # 縛りなし
            troll_content = "自由にプレイ"
            rarity = "-"

        results.append({
            "role": role,                     
            "summoner": shuffled_summoners[i],
            "champ": champ_jp,
            "champ_img": img_url,
            "troll": troll_content,
            "rarity": rarity,
        })

    return render(request, "gacha/result.html", {"results": results})