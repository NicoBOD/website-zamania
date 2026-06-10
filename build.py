import os
import re

slug = "fiabilisez-pipeline-ia-crm-echanges-clients"

# Data for FR
fr_title = "Fiabilisez votre pipeline : laissez l'IA mettre à jour votre CRM à partir des échanges clients"
fr_date = "9 Juin 2026"
fr_desc = "Connectez un agent IA aux courriels et comptes rendus d'appels pour actualiser les statuts, détecter les signaux de perte et ajuster les prévisions commerciales."
fr_sommaire = """<li><a href="#le-probleme">Des données de pilotage déconnectées de la réalité terrain</a></li>
<li><a href="#la-solution">Un agent IA connecté aux flux commerciaux</a></li>
<li><a href="#les-benefices">Des prévisions exactes, des commerciaux qui vendent</a></li>"""
fr_content = """<h2 id="le-probleme">Des données de pilotage déconnectées de la réalité terrain</h2>
<p>Les commerciaux détestent la saisie CRM. Ils repoussent cette tâche en fin de semaine ou bâclent les comptes rendus pour retourner vendre. Résultat : la direction pilote l'entreprise avec des données périmées. Les prévisions de vente (pipeline) deviennent des estimations subjectives. Vous découvrez qu'une affaire est perdue trois semaines après le courriel du client. Ce décalage complique l'allocation des ressources et fausse les objectifs financiers.</p>

<h2 id="la-solution">Un agent IA connecté aux flux commerciaux</h2>
<p>L'intelligence artificielle supprime la saisie manuelle. Un agent IA analyse directement les échanges avec les clients (courriels entrants et sortants, retranscriptions d'appels ou de visioconférences). Il identifie les avancées de chaque dossier.</p>
<p>Dès qu'un client exprime un frein, l'agent modifie le statut de l'opportunité dans le CRM. Lorsqu'un commercial envoie une proposition tarifaire, le système met à jour le montant et la date de clôture estimée. L'IA extrait les informations clés (nouveaux décideurs, budgets, délais) et remplit les champs appropriés sans intervention humaine.</p>

<h2 id="les-benefices">Des prévisions exactes, des commerciaux qui vendent</h2>
<p>L'automatisation du CRM sécurise vos revenus. La direction dispose de tableaux de bord fiables en temps réel pour prendre des décisions d'investissement pertinentes. Les managers identifient immédiatement les dossiers bloqués et interviennent avant que le client ne signe chez un concurrent.</p>
<p>Surtout, vos commerciaux récupèrent plusieurs heures par semaine. Ils concentrent leur énergie sur la négociation et la relance plutôt que sur le travail administratif. L'entreprise aligne enfin sa réalité terrain avec les données de son système d'information.</p>"""

# Data for EN
en_title = "Secure Your Pipeline: Let AI Update Your CRM from Client Communications"
en_date = "June 9, 2026"
en_desc = "Connect an AI agent to emails and call summaries to update statuses, detect loss signals, and adjust sales forecasts."
en_sommaire = """<li><a href="#the-problem">Management data disconnected from field reality</a></li>
<li><a href="#the-solution">An AI agent connected to sales workflows</a></li>
<li><a href="#the-benefits">Accurate forecasts, salespeople who actually sell</a></li>"""
en_content = """<h2 id="the-problem">Management data disconnected from field reality</h2>
<p>Salespeople hate CRM data entry. They push this task to the end of the week or rush through meeting notes so they can get back to selling. As a result, management steers the company using outdated data. Sales forecasts (pipeline) become subjective estimates. You discover a deal is lost three weeks after the client's email. This lag complicates resource allocation and distorts financial targets.</p>

<h2 id="the-solution">An AI agent connected to sales workflows</h2>
<p>Artificial intelligence eliminates manual data entry. An AI agent directly analyzes client communications (inbound and outbound emails, call transcripts, video meeting summaries). It tracks the progress of every deal.</p>
<p>As soon as a client mentions an obstacle, the agent updates the opportunity status in the CRM. When a sales rep sends a pricing proposal, the system adjusts the projected amount and expected close date. The AI extracts key information (new decision-makers, budgets, deadlines) and fills out the relevant fields with zero human intervention.</p>

<h2 id="the-benefits">Accurate forecasts, salespeople who actually sell</h2>
<p>CRM automation secures your revenue. Management accesses reliable, real-time dashboards to make informed investment decisions. Managers immediately spot stalled deals and step in before the prospect signs with a competitor.</p>
<p>Most importantly, your sales team reclaims hours every week. They focus their energy on negotiating and following up rather than doing administrative work. The company finally aligns its field reality with the data in its information systems.</p>"""

# Data for AR
ar_title = "تأمين مسار المبيعات: دع الذكاء الاصطناعي يحدّث نظام إدارة علاقات العملاء بناءً على المراسلات"
ar_date = "9 يونيو 2026"
ar_desc = "اربط وكيل الذكاء الاصطناعي برسائل البريد الإلكتروني وملخصات المكالمات لتحديث الحالات، واكتشاف إشارات الرفض، وتعديل توقعات المبيعات."
ar_sommaire = """<li><a href="#the-problem">بيانات إدارية منفصلة عن واقع الميدان</a></li>
<li><a href="#the-solution">وكيل ذكاء اصطناعي متصل بمسارات المبيعات</a></li>
<li><a href="#the-benefits">توقعات دقيقة، ومندوبو مبيعات يركزون على البيع</a></li>"""
ar_content = """<h2 id="the-problem">بيانات إدارية منفصلة عن واقع الميدان</h2>
<p>يكره مندوبو المبيعات إدخال البيانات في نظام إدارة علاقات العملاء (CRM). يؤجلون هذه المهمة إلى نهاية الأسبوع أو يكتبون ملخصات الاجتماعات على عجل للعودة إلى البيع. النتيجة: تدير الإدارة الشركة باستخدام بيانات قديمة. تتحول توقعات المبيعات إلى تقديرات شخصية. تكتشف أن صفقة ما قد ضاعت بعد ثلاثة أسابيع من استلام رسالة العميل. هذا التأخير يعقد تخصيص الموارد ويشوه الأهداف المالية.</p>

<h2 id="the-solution">وكيل ذكاء اصطناعي متصل بمسارات المبيعات</h2>
<p>الذكاء الاصطناعي يلغي الحاجة إلى الإدخال اليدوي. يقوم وكيل الذكاء الاصطناعي بتحليل تواصل العملاء مباشرة (رسائل البريد الإلكتروني الواردة والصادرة، تفريغ المكالمات، وملخصات الفيديو). يتتبع تقدم كل صفقة بدقة.</p>
<p>بمجرد أن يذكر العميل عائقاً ما، يحدّث الوكيل حالة الفرصة في النظام. وعندما يرسل مندوب المبيعات عرض سعر، يعدّل النظام المبلغ المتوقع وتاريخ الإغلاق المحتمل. يستخرج الذكاء الاصطناعي المعلومات الأساسية (صناع القرار الجدد، الميزانيات، المواعيد النهائية) ويملأ الحقول المناسبة دون تدخل بشري.</p>

<h2 id="the-benefits">توقعات دقيقة، ومندوبو مبيعات يركزون على البيع</h2>
<p>أتمتة نظام إدارة علاقات العملاء تؤمن إيراداتك. تحصل الإدارة على لوحات معلومات موثوقة في الوقت الفعلي لاتخاذ قرارات استثمارية. يكتشف المديرون فوراً الصفقات المتعثرة ويتدخلون قبل أن يوقع العميل مع منافس.</p>
<p>الأهم من ذلك، يستعيد فريق المبيعات ساعات طويلة أسبوعياً. يركزون طاقتهم على التفاوض والمتابعة بدلاً من الأعمال الإدارية. وأخيراً، تطابق الشركة واقعها الميداني مع بيانات أنظمة المعلومات.</p>"""

def process_template(template_path, out_path, title, date, desc, sommaire, content, image_url):
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{DATE}}', date)
    html = html.replace('{{DESCRIPTION}}', desc)
    html = html.replace('{{SOMMAIRE}}', sommaire)
    html = html.replace('{{CONTENT}}', content)
    html = html.replace('{{IMAGE_URL}}', image_url)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

process_template('/opt/data/website-zamania/blog/template.html', f'/opt/data/website-zamania/blog/{slug}.html', fr_title, fr_date, fr_desc, fr_sommaire, fr_content, f'../images/blog/img-ia-crm-donnees-pipeline.jpg')

process_template('/opt/data/website-zamania/en/blog/template.html', f'/opt/data/website-zamania/en/blog/{slug}.html', en_title, en_date, en_desc, en_sommaire, en_content, f'../../images/blog/img-ia-crm-donnees-pipeline.jpg')

process_template('/opt/data/website-zamania/ar/blog/template.html', f'/opt/data/website-zamania/ar/blog/{slug}.html', ar_title, ar_date, ar_desc, ar_sommaire, ar_content, f'../../images/blog/img-ia-crm-donnees-pipeline.jpg')

# Update indexes
def insert_in_index(index_path, card_html):
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    parts = html.split('<!-- ARTICLES_LIST_START -->')
    if len(parts) == 2:
        new_html = parts[0] + '<!-- ARTICLES_LIST_START -->\n' + card_html + parts[1]
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_html)

fr_card = f'''                <article class="blog-card">
                    <img src="../images/blog/img-ia-crm-donnees-pipeline.jpg" alt="{fr_title}" class="blog-card-img">
                    <div class="blog-card-content">
                        <span class="blog-card-date">{fr_date}</span>
                        <h3><a href="{slug}.html">{fr_title}</a></h3>
                        <p>{fr_desc}</p>
                        <a href="{slug}.html" class="read-more">Lire l'article →</a>
                    </div>
                </article>\n'''

en_card = f'''                <article class="blog-card">
                    <img src="../../images/blog/img-ia-crm-donnees-pipeline.jpg" alt="{en_title}" class="blog-card-img">
                    <div class="blog-card-content">
                        <span class="blog-card-date">{en_date}</span>
                        <h3><a href="{slug}.html">{en_title}</a></h3>
                        <p>{en_desc}</p>
                        <a href="{slug}.html" class="read-more">Read article →</a>
                    </div>
                </article>\n'''

ar_card = f'''                <article class="blog-card">
                    <img src="../../images/blog/img-ia-crm-donnees-pipeline.jpg" alt="{ar_title}" class="blog-card-img">
                    <div class="blog-card-content">
                        <span class="blog-card-date">{ar_date}</span>
                        <h3><a href="{slug}.html">{ar_title}</a></h3>
                        <p>{ar_desc}</p>
                        <a href="{slug}.html" class="read-more">اقرأ المقال ←</a>
                    </div>
                </article>\n'''

insert_in_index('/opt/data/website-zamania/blog/index.html', fr_card)
insert_in_index('/opt/data/website-zamania/en/blog/index.html', en_card)
insert_in_index('/opt/data/website-zamania/ar/blog/index.html', ar_card)

print("Pages created and indexes updated.")
