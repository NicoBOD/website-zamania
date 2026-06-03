import json
from datetime import datetime

# Information from proposal 1
title_fr = "Service client sous tension ? Divisez par deux votre temps de réponse grâce au tri automatisé"
title_en = "Customer Service Under Pressure? Halve Your Response Time with Automated Triage"
title_ar = "خدمة العملاء تحت الضغط؟ اخفض وقت الاستجابة للنصف بفضل الفرز الآلي"

slug = "service-client-tri-automatise"
date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+02:00")
date_fr = datetime.now().strftime("%d %B %Y")
date_en = datetime.now().strftime("%B %d, %Y")
date_ar = datetime.now().strftime("%d مايو %Y").replace("مايو", "يونيو") # Hardcoding to June for simplicity if 06

content_fr = """
<p>Face à des volumes de demandes croissants, les équipes de support client se retrouvent souvent submergées. Traiter chaque ticket manuellement, de la lecture à la catégorisation jusqu'à la rédaction de la réponse, est un gouffre de temps et d'énergie. L'automatisation intelligente offre une solution ROIste pour diviser par deux le temps de réponse tout en allégeant la charge mentale de vos agents.</p>

<h2>Le coût caché du tri manuel des tickets</h2>
<p>Chaque minute passée par un agent à lire, comprendre et attribuer un ticket est une minute qui n'est pas consacrée à la résolution du problème. Ce travail de pré-catégorisation ralentit la réactivité globale, crée des goulots d'étranglement et nuit à l'expérience client. Dans un environnement B2B, la réactivité est un avantage concurrentiel direct, influençant directement la fidélisation.</p>

<h2>L'automatisation intelligente au service des agents</h2>
<p>L'intelligence artificielle ne remplace pas le support client, elle l'augmente. Un système automatisé de tri intelligent agit comme un filtre puissant dès la réception du ticket :</p>
<ul>
    <li><strong>Pré-catégorisation instantanée :</strong> Analyse sémantique de la demande pour l'orienter vers le bon service ou la bonne compétence.</li>
    <li><strong>Priorisation automatique :</strong> Détection du niveau d'urgence, de la tonalité du client, ou de l'importance du compte.</li>
    <li><strong>Pré-rédaction de réponses :</strong> Suggestion de modèles de réponses pertinents basés sur l'historique et la base de connaissances.</li>
</ul>

<h2>Un retour sur investissement immédiat</h2>
<p>En automatisant ces tâches répétitives, l'impact sur les KPIs est direct. Le temps moyen de première réponse (FRT) chute drastiquement, le temps de résolution globale s'améliore, et la satisfaction client grimpe. Les équipes, libérées du travail de saisie, se concentrent sur la résolution de problèmes complexes, offrant une qualité de service supérieure.</p>

<p>Ne laissez plus vos agents s'épuiser sur des tâches chronophages. Transformez votre service client en un centre de création de valeur et fidélisez durablement vos clients.</p>

<div class="cta-box">
    <h3>Prêt à optimiser votre support client ?</h3>
    <p>Découvrez comment nos solutions IA peuvent s'intégrer à vos outils actuels pour un ROI rapide et mesurable.</p>
    <a href="mailto:contact@zamania.fr" class="btn btn-primary">contact@zamania.fr</a>
</div>
"""

content_en = """
<p>Faced with growing volumes of requests, customer support teams often find themselves overwhelmed. Processing every ticket manually—from reading and categorizing to drafting a response—is a massive drain on time and energy. Intelligent automation offers an ROI-focused solution to halve response times while reducing your agents' mental workload.</p>

<h2>The Hidden Cost of Manual Ticket Triage</h2>
<p>Every minute an agent spends reading, understanding, and routing a ticket is a minute not spent resolving the problem. This pre-categorization work slows down overall responsiveness, creates bottlenecks, and harms the customer experience. In a B2B environment, responsiveness is a direct competitive advantage, directly influencing retention.</p>

<h2>Intelligent Automation Empowering Agents</h2>
<p>Artificial Intelligence doesn't replace customer support; it augments it. An automated, intelligent triage system acts as a powerful filter the moment a ticket is received:</p>
<ul>
    <li><strong>Instant Pre-categorization:</strong> Semantic analysis of the request to route it to the right department or skill set.</li>
    <li><strong>Automatic Prioritization:</strong> Detection of urgency level, customer sentiment, or account importance.</li>
    <li><strong>Drafting Responses:</strong> Suggesting relevant response templates based on history and the knowledge base.</li>
</ul>

<h2>Immediate Return on Investment</h2>
<p>By automating these repetitive tasks, the impact on KPIs is direct. The First Response Time (FRT) drops drastically, overall resolution time improves, and customer satisfaction soars. Teams, freed from data entry work, focus on solving complex problems, delivering superior service quality.</p>

<p>Stop letting your agents burn out on time-consuming tasks. Transform your customer service into a value creation center and build lasting customer loyalty.</p>

<div class="cta-box">
    <h3>Ready to Optimize Your Customer Support?</h3>
    <p>Discover how our AI solutions can integrate with your current tools for a fast, measurable ROI.</p>
    <a href="mailto:contact@zamania.fr" class="btn btn-primary">contact@zamania.fr</a>
</div>
"""

content_ar = """
<p>في ظل تزايد حجم الطلبات، غالباً ما تجد فرق دعم العملاء نفسها غارقة في العمل. إن معالجة كل تذكرة يدوياً - من القراءة والتصنيف إلى صياغة الرد - هي استنزاف هائل للوقت والجهد. توفر الأتمتة الذكية حلاً يركز على العائد على الاستثمار لخفض أوقات الاستجابة إلى النصف مع تخفيف العبء الذهني عن موظفيك.</p>

<h2>التكلفة الخفية للفرز اليدوي للتذاكر</h2>
<p>كل دقيقة يقضيها الموظف في قراءة التذكرة وفهمها وتوجيهها هي دقيقة لا يتم قضاؤها في حل المشكلة. يؤدي عمل التصنيف المسبق هذا إلى إبطاء الاستجابة الشاملة، وخلق اختناقات، والإضرار بتجربة العملاء. في بيئة التعاملات بين الشركات (B2B)، تعد الاستجابة السريعة ميزة تنافسية مباشرة تؤثر بشكل مباشر على الاحتفاظ بالعملاء.</p>

<h2>الأتمتة الذكية لتمكين الموظفين</h2>
<p>الذكاء الاصطناعي لا يحل محل دعم العملاء، بل يعززه. يعمل نظام الفرز الآلي الذكي كفلتر قوي بمجرد استلام التذكرة:</p>
<ul>
    <li><strong>تصنيف مسبق فوري:</strong> تحليل دلالي للطلب لتوجيهه إلى القسم المناسب أو ذوي المهارات المطلوبة.</li>
    <li><strong>تحديد الأولويات التلقائي:</strong> اكتشاف مستوى الأهمية، ومشاعر العميل، أو أهمية الحساب.</li>
    <li><strong>صياغة الردود:</strong> اقتراح قوالب الردود ذات الصلة بناءً على السجل وقاعدة المعرفة.</li>
</ul>

<h2>عائد استثمار فوري</h2>
<p>من خلال أتمتة هذه المهام المتكررة، يكون التأثير على مؤشرات الأداء الرئيسية مباشراً. ينخفض وقت الاستجابة الأول (FRT) بشكل كبير، ويتحسن وقت الحل الإجمالي، وترتفع معدلات رضا العملاء. الفرق، التي تحررت من أعمال إدخال البيانات، تركز على حل المشكلات المعقدة، وتقديم جودة خدمة فائقة.</p>

<p>لا تدع موظفيك يرهقون أنفسهم في المهام المستهلكة للوقت. حوّل خدمة العملاء إلى مركز لخلق القيمة وابنِ ولاءً دائماً للعملاء.</p>

<div class="cta-box">
    <h3>هل أنت مستعد لتحسين دعم العملاء؟</h3>
    <p>اكتشف كيف يمكن لحلول الذكاء الاصطناعي لدينا أن تتكامل مع أدواتك الحالية لتحقيق عائد استثمار سريع وقابل للقياس.</p>
    <a href="mailto:contact@zamania.fr" class="btn btn-primary">contact@zamania.fr</a>
</div>
"""

summary_fr = "Comment un système intelligent pré-catégorise, priorise et pré-rédige les réponses pour le support client, améliorant l'expérience sans surcharger l'équipe."
summary_en = "How an intelligent system pre-categorizes, prioritizes, and drafts responses for customer support, improving the experience without overloading the team."
summary_ar = "كيف يقوم نظام ذكي بتصنيف الردود مسبقاً وتحديد أولوياتها وصياغتها لدعم العملاء، مما يحسن التجربة دون إثقال كاهل الفريق."

import os

def create_page(template_path, target_path, title, date_formatted, summary, content, img_url):
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{DATE}}', date_formatted)
    html = html.replace('{{DESCRIPTION}}', summary)
    html = html.replace('{{SOMMAIRE}}', summary)
    html = html.replace('{{CONTENT}}', content)
    html = html.replace('{{IMAGE_URL}}', img_url)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(html)

def update_index(index_path, title, date_formatted, summary, slug, img_url):
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Simple card html
    card_html = f"""
            <article class="blog-card">
                <img src="{img_url}" alt="{title}">
                <div class="blog-card-content">
                    <span class="blog-card-date">{date_formatted}</span>
                    <h3>{title}</h3>
                    <p>{summary}</p>
                    <a href="{slug}.html">Lire l'article</a>
                </div>
            </article>"""
            
    # Modify "Lire l'article" for EN and AR
    if "en/blog" in index_path:
        card_html = card_html.replace("Lire l'article", "Read article")
    elif "ar/blog" in index_path:
        card_html = card_html.replace("Lire l'article", "اقرأ المقال")
    
    new_html = html.replace('<!-- ARTICLES_LIST_START -->', '<!-- ARTICLES_LIST_START -->' + card_html)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

# FR
create_page(
    '/opt/data/website-zamania/blog/template.html',
    f'/opt/data/website-zamania/blog/{slug}.html',
    title_fr, date_fr, summary_fr, content_fr, f"../images/blog/img-{slug}.jpg"
)
update_index('/opt/data/website-zamania/blog/index.html', title_fr, date_fr, summary_fr, slug, f"../images/blog/img-{slug}.jpg")

# EN
create_page(
    '/opt/data/website-zamania/en/blog/template.html',
    f'/opt/data/website-zamania/en/blog/{slug}.html',
    title_en, date_en, summary_en, content_en, f"../../images/blog/img-{slug}.jpg"
)
update_index('/opt/data/website-zamania/en/blog/index.html', title_en, date_en, summary_en, slug, f"../../images/blog/img-{slug}.jpg")

# AR
create_page(
    '/opt/data/website-zamania/ar/blog/template.html',
    f'/opt/data/website-zamania/ar/blog/{slug}.html',
    title_ar, date_ar, summary_ar, content_ar, f"../../images/blog/img-{slug}.jpg"
)
update_index('/opt/data/website-zamania/ar/blog/index.html', title_ar, date_ar, summary_ar, slug, f"../../images/blog/img-{slug}.jpg")

print(f"Generated {slug} across FR, EN, AR.")
