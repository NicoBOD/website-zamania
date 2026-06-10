import os
import json
import datetime
import subprocess

slug = "accelerez-signatures-propositions-commerciales"

# Constants
DATE_FR = "10 Juin 2026"
DATE_EN = "June 10, 2026"
DATE_AR = "10 يونيو 2026"

TITLE_FR = "Accélérez vos signatures : générez des propositions commerciales sur mesure le jour même"
TITLE_EN = "Accelerate Your Signatures: Generate Custom Proposals on the Same Day"
TITLE_AR = "تسريع التوقيعات: صياغة عروض تجارية مخصصة في نفس اليوم"

DESC_FR = "Divisez par dix votre temps de réponse aux appels d'offres. Découvrez comment l'IA analyse les cahiers des charges et rédige vos propositions commerciales sur mesure le jour même."
DESC_EN = "Cut your response time to tenders by ten. Discover how AI analyzes specifications and drafts custom proposals on the same day."
DESC_AR = "قسّم وقت الاستجابة للمناقصات على عشرة. اكتشف كيف يحلل الذكاء الاصطناعي المواصفات ويصوغ عروضك التجارية المخصصة في نفس اليوم."

IMG_URL_FR = f"../images/blog/img-{slug}.jpg"
IMG_URL_EN_AR = f"../../images/blog/img-{slug}.jpg"

SOMMAIRE_FR = """<li><a href="#delai-de-reponse">Le délai de réponse détruit vos conversions</a></li>
<li><a href="#analyse-millimetree">Une analyse millimétrée de chaque demande</a></li>
<li><a href="#reactivite-avantage">La réactivité comme avantage compétitif</a></li>"""

SOMMAIRE_EN = """<li><a href="#response-time">Response Time Destroys Conversions</a></li>
<li><a href="#pinpoint-analysis">Pinpoint Analysis of Every Request</a></li>
<li><a href="#speed-advantage">Gain Market Share Through Speed</a></li>"""

SOMMAIRE_AR = """<li><a href="#response-time">وقت الاستجابة يدمر التحويلات</a></li>
<li><a href="#pinpoint-analysis">تحليل دقيق لكل طلب</a></li>
<li><a href="#speed-advantage">اكتساب حصة في السوق من خلال السرعة</a></li>"""

CONTENT_FR = """<p>Vous perdez des affaires à cause des délais de réponse. Vos équipes commerciales passent des heures à décortiquer des cahiers des charges. Ils copient des clauses contractuelles pendant que les clients attendent. La concurrence prend l'avantage. Une intelligence artificielle inverse cette dynamique. Elle analyse les demandes complexes et produit une proposition chiffrée en quelques minutes.</p>

<h2 id="delai-de-reponse">Le délai de réponse détruit vos conversions</h2>
<p>Les acheteurs B2B décident vite. Un prospect qui consulte trois prestataires retient le premier qui livre une proposition claire et adaptée. L'analyse manuelle des exigences ralentit vos ventes. Les commerciaux épuisent leur énergie sur la rédaction administrative. La fatigue crée des erreurs dans les devis.</p>

<h2 id="analyse-millimetree">Une analyse millimétrée de chaque demande</h2>
<p>Un agent IA ingère vos documents entrants. Il isole les exigences techniques. Il extrait les contraintes légales. Le système relie ces éléments à votre catalogue de services. Il rédige une réponse personnalisée. Vos commerciaux n'ont plus qu'à valider le document final. Le temps de traitement passe de trois jours à trois heures.</p>

<h2 id="reactivite-avantage">La réactivité comme avantage compétitif</h2>
<p>La vitesse de réponse devient votre argument majeur. Une entreprise qui chiffre un projet complexe le jour même impose son rythme. Vous saturez le marché. Vous augmentez la capacité de traitement de votre équipe commerciale à effectif constant. Vous signez plus de contrats.</p>"""

CONTENT_EN = """<p>You lose deals because of slow response times. Your sales teams spend hours dissecting specifications. They copy and paste contract clauses while clients wait. Competitors take the lead. Artificial intelligence reverses this dynamic. It analyzes complex requests and produces a costed proposal in minutes.</p>

<h2 id="response-time">Response Time Destroys Conversions</h2>
<p>B2B buyers make fast decisions. A prospect consulting three vendors selects the first one delivering a clear proposal. Manual analysis of requirements slows down your sales. Salespeople burn their energy on administrative drafting. Fatigue introduces errors into quotes.</p>

<h2 id="pinpoint-analysis">Pinpoint Analysis of Every Request</h2>
<p>An AI agent ingests your incoming documents. It isolates technical requirements. It extracts legal constraints. The system links these elements to your service catalog. It drafts a customized response. Your salespeople just validate the final document. Processing time drops from three days to three hours.</p>

<h2 id="speed-advantage">Gain Market Share Through Speed</h2>
<p>Speed of response becomes your primary weapon. A company quoting a complex project the same day dictates the tempo. You capture market share. You increase your sales team's capacity without adding headcount. You sign more contracts.</p>"""

CONTENT_AR = """<p>تفقد الصفقات بسبب بطء أوقات الاستجابة. تقضي فرق المبيعات لديك ساعات في دراسة المواصفات. ينسخون الشروط التعاقدية بينما ينتظر العملاء. المنافسون يأخذون زمام المبادرة. الذكاء الاصطناعي يعكس هذه الديناميكية. يحلل الطلبات المعقدة وينتج عرضًا مسعرًا في دقائق.</p>

<h2 id="response-time">وقت الاستجابة يدمر التحويلات</h2>
<p>يتخذ مشتري B2B قرارات سريعة. يختار العميل المحتمل الذي يستشير ثلاثة موردين أول من يقدم عرضًا واضحًا. التحليل اليدوي للمتطلبات يبطئ مبيعاتك. يستنزف مندوبو المبيعات طاقتهم في الصياغة الإدارية. التعب يدخل الأخطاء في عروض الأسعار.</p>

<h2 id="pinpoint-analysis">تحليل دقيق لكل طلب</h2>
<p>يستوعب وكيل الذكاء الاصطناعي مستنداتك الواردة. يعزل المتطلبات الفنية. يستخرج القيود القانونية. يربط النظام هذه العناصر بكتالوج الخدمات الخاص بك. يصيغ استجابة مخصصة. يقوم مندوبو المبيعات لديك فقط بالتحقق من صحة المستند النهائي. ينخفض وقت المعالجة من ثلاثة أيام إلى ثلاث ساعات.</p>

<h2 id="speed-advantage">اكتساب حصة في السوق من خلال السرعة</h2>
<p>تصبح سرعة الاستجابة سلاحك الأساسي. تفرض الشركة التي تسعر مشروعًا معقدًا في نفس اليوم إيقاعها. أنت تستحوذ على حصة في السوق. تزيد من قدرة فريق المبيعات لديك دون زيادة عدد الموظفين. توقع المزيد من العقود.</p>"""

def process_file(template_path, target_path, title, date, desc, image_url, sommaire, content):
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DATE}}", date)
    html = html.replace("{{DESCRIPTION}}", desc)
    html = html.replace("{{IMAGE_URL}}", image_url)
    html = html.replace("{{SOMMAIRE}}", sommaire)
    html = html.replace("{{CONTENT}}", content)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html)

base_path = "/opt/data/website-zamania"
process_file(f"{base_path}/blog/template.html", f"{base_path}/blog/{slug}.html", TITLE_FR, DATE_FR, DESC_FR, IMG_URL_FR, SOMMAIRE_FR, CONTENT_FR)
process_file(f"{base_path}/en/blog/template.html", f"{base_path}/en/blog/{slug}.html", TITLE_EN, DATE_EN, DESC_EN, IMG_URL_EN_AR, SOMMAIRE_EN, CONTENT_EN)
process_file(f"{base_path}/ar/blog/template.html", f"{base_path}/ar/blog/{slug}.html", TITLE_AR, DATE_AR, DESC_AR, IMG_URL_EN_AR, SOMMAIRE_AR, CONTENT_AR)

# Update index files
def update_index(index_path, title, date, desc, slug, is_root=True):
    with open(index_path, "r", encoding="utf-8") as f:
        idx = f.read()
    
    # Read the text for the button and image path
    img_prefix = "../images" if is_root else "../../images"
    btn_text = "Lire l'article" if is_root else ("Read article" if "/en/" in index_path else "اقرأ المقال")
    
    card = f"""
            <article class="blog-card">
                <img src="{img_prefix}/blog/img-{slug}.jpg" alt="{title}">
                <div class="blog-card-content">
                    <span class="blog-card-date">{date}</span>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                    <a href="{slug}.html">{btn_text}</a>
                </div>
            </article>
"""
    idx = idx.replace("<!-- ARTICLES_LIST_START -->", f"<!-- ARTICLES_LIST_START -->\n{card}")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(idx)

update_index(f"{base_path}/blog/index.html", TITLE_FR, DATE_FR, DESC_FR, slug, True)
update_index(f"{base_path}/en/blog/index.html", TITLE_EN, DATE_EN, DESC_EN, slug, False)
update_index(f"{base_path}/ar/blog/index.html", TITLE_AR, DATE_AR, DESC_AR, slug, False)

# Write to zamania-selection.json
sel_path = f"{base_path}/.automation/zamania-selection.json"
now_iso = datetime.datetime.now().astimezone().isoformat()
with open(sel_path, "r", encoding="utf-8") as f:
    sel = json.load(f)
sel["status"] = "published"
sel["published_at"] = now_iso
sel["slug"] = slug
sel["links"] = {
    "fr": f"https://zamania.fr/blog/{slug}.html",
    "en": f"https://zamania.fr/en/blog/{slug}.html",
    "ar": f"https://zamania.fr/ar/blog/{slug}.html"
}
sel["choice"] = "2"
sel["proposal_date"] = "2026-06-09"
with open(sel_path, "w", encoding="utf-8") as f:
    json.dump(sel, f, indent=2)

print("Files generated and index updated.")
