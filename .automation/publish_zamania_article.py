from __future__ import annotations

import json
import math
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

BASE = Path('/opt/data/website-zamania')
SELECTION_PATH = BASE / '.automation' / 'zamania-selection.json'
SESSIONS_INDEX_PATH = Path('/opt/data/sessions/sessions.json')
TELEGRAM_CHAT_ID = '1108946227'
MARKER = '🗂️ Propositions ZamanIA du jour'
SLUG = 'cout-cache-taches-repetitives-marge-entreprise'
IMAGE_NAME = f'img-{SLUG}.jpg'
IMAGE_PATH = BASE / 'images' / 'blog' / IMAGE_NAME
TODAY = datetime.now().astimezone()
TODAY_ISO_DATE = TODAY.date().isoformat()
MARKER_HTML = '<!-- ARTICLES_LIST_START -->'

ARTICLE = {
    'choice_label': '1',
    'subject_fr': 'Combien les tâches répétitives coûtent-elles réellement à votre entreprise ?',
    'slug': SLUG,
    'title_fr': 'Le coût caché des tâches répétitives : la fuite silencieuse de marge dans votre entreprise',
    'title_en': 'The Hidden Cost of Repetitive Tasks: The Silent Margin Drain in Your Business',
    'title_ar': 'التكلفة الخفية للمهام المتكررة: النزيف الصامت لهامش الربح في شركتك',
    'description_fr': "Derrière les micro-tâches répétitives se cache une perte mensuelle de marge, de réactivité et de capacité. Voici comment la mesurer et où automatiser en priorité.",
    'description_en': 'Behind repetitive micro-tasks lies a monthly loss of margin, responsiveness, and capacity. Here is how to measure it and where to automate first.',
    'description_ar': 'خلف المهام الصغيرة المتكررة توجد خسارة شهرية في الهامش والسرعة والقدرة التشغيلية. إليك كيف تقيسها وأين تبدأ الأتمتة أولاً.',
    'date_fr': '1 Juin 2026',
    'date_en': 'June 1, 2026',
    'date_ar': '1 يونيو 2026',
    'sommaire_fr': [
        ('structural-cost', '1. Ce qui transforme quelques minutes en coût structurel'),
        ('calculate-loss', '2. Une méthode simple pour calculer la perte mensuelle'),
        ('business-examples', '3. Des exemples concrets par service'),
        ('real-cost', '4. Pourquoi le coût réel dépasse la masse salariale'),
        ('where-to-start', '5. Où automatiser en priorité pour récupérer de la marge'),
    ],
    'sommaire_en': [
        ('structural-cost', '1. What turns a few minutes into a structural cost'),
        ('calculate-loss', '2. A simple way to calculate the monthly loss'),
        ('business-examples', '3. Concrete examples by department'),
        ('real-cost', '4. Why the real cost goes beyond payroll'),
        ('where-to-start', '5. Where to automate first to recover margin'),
    ],
    'sommaire_ar': [
        ('structural-cost', '1. ما الذي يحول بضع دقائق إلى تكلفة هيكلية'),
        ('calculate-loss', '2. طريقة بسيطة لحساب الخسارة الشهرية'),
        ('business-examples', '3. أمثلة عملية حسب الأقسام'),
        ('real-cost', '4. لماذا تتجاوز الكلفة الحقيقية بند الرواتب'),
        ('where-to-start', '5. أين تبدأ الأتمتة لاستعادة الهامش'),
    ],
    'content_fr': """
<p>Dans beaucoup d'entreprises, la perte de marge ne vient pas d'une seule grosse inefficacité. Elle vient d'une accumulation invisible : copier des informations d'un outil à l'autre, reformater un reporting, relancer un client avec un message standard, vérifier manuellement une pièce jointe, mettre à jour le CRM après chaque échange. Individuellement, ces tâches paraissent mineures. À l'échelle d'une semaine, d'un service ou d'une année, elles deviennent une fuite silencieuse de temps, d'argent et de capacité.</p>
<p>Pour un dirigeant, l'enjeu n'est pas seulement opérationnel. C'est un sujet de rentabilité. Chaque minute absorbée par une micro-tâche répétitive est une minute qui n'est pas consacrée à la vente, au service client, au suivi des dossiers sensibles ou au pilotage. La bonne nouvelle : ce coût se calcule vite, et il se réduit souvent vite aussi avec une automatisation IA bien ciblée.</p>

<h2 id="structural-cost">1. Ce qui transforme quelques minutes en coût structurel</h2>
<p>Le piège des tâches répétitives, c'est qu'elles sont dispersées. Elles n'apparaissent pas comme un projet, mais comme une habitude de travail. Pourtant, elles produisent un coût structurel pour trois raisons :</p>
<ul>
    <li><strong>elles cassent la concentration</strong> et multiplient les changements de contexte ;</li>
    <li><strong>elles rallongent chaque cycle métier</strong>, car chaque dossier dépend d'une intervention manuelle supplémentaire ;</li>
    <li><strong>elles immobilisent des profils qualifiés</strong> sur des actions à faible valeur ajoutée.</li>
</ul>
<p>Autrement dit, même quand personne n'a l'impression de perdre une heure, l'entreprise additionne chaque semaine des dizaines d'heures qui ne créent ni marge supplémentaire ni avantage concurrentiel.</p>

<h2 id="calculate-loss">2. Une méthode simple pour calculer la perte mensuelle</h2>
<p>La formule de base est simple : <strong>nombre de personnes concernées × temps perdu par jour × coût horaire chargé × jours travaillés</strong>.</p>
<p>Prenons un cas réaliste : <strong>12 collaborateurs</strong> perdent chacun <strong>35 minutes par jour</strong> sur des tâches répétitives, avec un coût chargé moyen de <strong>29 € par heure</strong>, sur <strong>220 jours travaillés</strong> par an. Le coût atteint alors <strong>44 660 € par an</strong>, soit environ <strong>3 722 € par mois</strong>.</p>
<p>Et ce calcul ne prend même pas encore en compte les corrections, les retards, les doublons ou les opportunités traitées trop tard. C'est pour cela qu'un irritant opérationnel apparemment banal devient, vu du dirigeant, un vrai sujet de marge.</p>

<h2 id="business-examples">3. Des exemples concrets par service</h2>
<h3>Commercial et administration des ventes</h3>
<p>Une équipe de <strong>10 personnes</strong> qui passe <strong>30 minutes par jour</strong> à ressaisir des informations, mettre à jour le CRM ou envoyer des relances standard immobilise déjà <strong>31 900 € par an</strong> avec un coût chargé de <strong>29 € par heure</strong>. Ce temps n'est plus consacré à la conversion ni au suivi des comptes prioritaires.</p>
<h3>Support client et opérations</h3>
<p>Dans une équipe de <strong>7 personnes</strong>, consacrer <strong>50 minutes par jour</strong> au tri des demandes, à la copie de statuts ou aux réponses répétitives représente près de <strong>35 933 € par an</strong> avec un coût horaire de <strong>28 €</strong>. Le coût financier s'ajoute alors à une expérience client plus lente.</p>
<h3>Finance et ressources humaines</h3>
<p>Collecte de pièces, contrôles, rapprochements, mises à jour de tableaux et relances internes : pour <strong>5 personnes</strong> perdant <strong>70 minutes par jour</strong> à <strong>34 € par heure</strong>, la facture monte à <strong>43 633 € par an</strong>. Dans ces fonctions, l'automatisation réduit à la fois le temps passé et le risque d'erreur.</p>

<h2 id="real-cost">4. Pourquoi le coût réel dépasse la masse salariale</h2>
<p>Le coût visible est celui du temps passé. Le coût réel va plus loin :</p>
<ul>
    <li><strong>les erreurs et ressaisies</strong> allongent encore davantage les traitements ;</li>
    <li><strong>les délais de réponse</strong> dégradent la satisfaction client et la qualité de service ;</li>
    <li><strong>les opportunités commerciales ratées</strong> pèsent sur le chiffre d'affaires quand les relances ou les devis partent trop tard ;</li>
    <li><strong>la fatigue opérationnelle</strong> réduit l'engagement sur les tâches à forte valeur.</li>
</ul>
<p>En pratique, une entreprise ne paie pas seulement des minutes perdues. Elle paie aussi une organisation plus lente, plus fragile et moins scalable.</p>

<h2 id="where-to-start">5. Où automatiser en priorité pour récupérer de la marge</h2>
<p>Les meilleurs projets d'automatisation IA ne commencent pas par les cas les plus impressionnants. Ils commencent par les séquences qui reviennent tous les jours, suivent des règles stables et passent d'un outil à l'autre. En pratique, les premières priorités sont souvent :</p>
<ul>
    <li>la qualification des demandes entrantes ;</li>
    <li>la collecte et la vérification de documents ;</li>
    <li>les mises à jour CRM, ERP ou tableaux internes ;</li>
    <li>les réponses standardisées et les relances simples ;</li>
    <li>la préparation de synthèses et reportings récurrents.</li>
</ul>
<p>Quand l'IA lit, classe, prépare, relance ou met à jour automatiquement, vos équipes gardent la validation finale mais récupèrent des heures utiles chaque semaine. C'est ainsi qu'on absorbe plus d'activité sans recruter trop tôt, tout en améliorant la réactivité et la marge.</p>
<p>Si vous voulez identifier les tâches répétitives qui pèsent le plus sur votre rentabilité, ZamanIA peut réaliser un audit rapide et concret de vos flux. Écrivez-nous à <strong>contact@zamania.fr</strong> pour chiffrer vos gains potentiels et prioriser les automatisations à plus fort ROI.</p>
""".strip(),
    'content_en': """
<p>In many companies, margin erosion does not come from one huge inefficiency. It comes from an invisible accumulation: copying information from one tool to another, reformatting a report, following up with a standard message, manually checking an attachment, updating the CRM after every exchange. Each task looks minor on its own. At the scale of a week, a department, or a year, it becomes a silent drain on time, money, and capacity.</p>
<p>For decision-makers, this is not just an operational issue. It is a profitability issue. Every minute absorbed by a repetitive micro-task is a minute not spent on selling, serving customers, handling sensitive cases, or leading the business. The good news is that this cost is easy to measure and, with well-targeted AI automation, often quick to reduce.</p>

<h2 id="structural-cost">1. What turns a few minutes into a structural cost</h2>
<p>The trap of repetitive tasks is that they are scattered. They do not look like a project. They look like routine. Yet they create a structural cost for three reasons:</p>
<ul>
    <li><strong>they break focus</strong> and multiply context switching;</li>
    <li><strong>they lengthen every business cycle</strong>, because each file or request depends on one more manual action;</li>
    <li><strong>they tie up qualified people</strong> on low-value work.</li>
</ul>
<p>In other words, even when nobody feels like they are losing an hour, the company is adding up dozens of hours every week that create neither additional margin nor competitive advantage.</p>

<h2 id="calculate-loss">2. A simple way to calculate the monthly loss</h2>
<p>The core formula is straightforward: <strong>number of people involved × time lost per day × loaded hourly cost × working days</strong>.</p>
<p>Take a realistic case: <strong>12 employees</strong> each lose <strong>35 minutes a day</strong> on repetitive tasks, with an average loaded cost of <strong>€29 per hour</strong>, across <strong>220 working days</strong> a year. That already adds up to <strong>€44,660 per year</strong>, or roughly <strong>€3,722 per month</strong>.</p>
<p>And that calculation does not yet include rework, delays, duplicates, or opportunities handled too late. That is why what feels like a small operational irritation becomes a real margin issue at leadership level.</p>

<h2 id="business-examples">3. Concrete examples by department</h2>
<h3>Sales and sales administration</h3>
<p>A team of <strong>10 people</strong> spending <strong>30 minutes a day</strong> re-entering information, updating the CRM, or sending standard follow-ups is already tying up <strong>€31,900 per year</strong> at a loaded cost of <strong>€29 per hour</strong>. That is time no longer spent on conversion or high-value accounts.</p>
<h3>Customer support and operations</h3>
<p>In a team of <strong>7 people</strong>, spending <strong>50 minutes a day</strong> sorting requests, copying statuses, or answering repetitive questions represents nearly <strong>€35,933 per year</strong> with an hourly cost of <strong>€28</strong>. The financial cost comes on top of a slower customer experience.</p>
<h3>Finance and human resources</h3>
<p>Document collection, checks, reconciliations, spreadsheet updates, and internal follow-ups quickly add up. For <strong>5 people</strong> losing <strong>70 minutes a day</strong> at <strong>€34 per hour</strong>, the bill reaches <strong>€43,633 per year</strong>. In these functions, automation reduces both time spent and error risk.</p>

<h2 id="real-cost">4. Why the real cost goes beyond payroll</h2>
<p>The visible cost is time spent. The real cost goes further:</p>
<ul>
    <li><strong>errors and re-entry</strong> create even more processing time;</li>
    <li><strong>slower response times</strong> reduce customer satisfaction and service quality;</li>
    <li><strong>missed sales opportunities</strong> hurt revenue when quotes or follow-ups go out too late;</li>
    <li><strong>operational fatigue</strong> lowers engagement on high-value work.</li>
</ul>
<p>In practice, a company is not only paying for lost minutes. It is also paying for a slower, more fragile, and less scalable operating model.</p>

<h2 id="where-to-start">5. Where to automate first to recover margin</h2>
<p>The best AI automation projects rarely start with the most spectacular use cases. They start with the sequences that happen every day, follow stable rules, and move data from one tool to another. In practice, the first priorities are often:</p>
<ul>
    <li>qualifying inbound requests;</li>
    <li>collecting and checking documents;</li>
    <li>updating CRM, ERP, or internal tracking tools;</li>
    <li>standardized replies and simple follow-ups;</li>
    <li>preparing recurring summaries and reports.</li>
</ul>
<p>When AI reads, classifies, prepares, follows up, or updates automatically, your teams keep final control while recovering useful hours every week. That is how you absorb more activity without hiring too early, while improving responsiveness and margin at the same time.</p>
<p>If you want to identify the repetitive tasks that weigh most heavily on your profitability, ZamanIA can run a fast, concrete audit of your workflows. Email <strong>contact@zamania.fr</strong> to quantify your potential gains and prioritize the automations with the highest ROI.</p>
""".strip(),
    'content_ar': """
<p>في كثير من الشركات، لا تأتي خسارة الهامش من مشكلة تشغيلية واحدة كبيرة، بل من تراكم غير مرئي: نسخ المعلومات من أداة إلى أخرى، إعادة تنسيق تقرير، متابعة عميل برسالة متشابهة، التحقق يدوياً من مرفق، أو تحديث نظام إدارة العملاء بعد كل تفاعل. كل مهمة بمفردها تبدو صغيرة، لكن على مستوى الأسبوع أو القسم أو السنة تتحول إلى نزيف صامت في الوقت والمال والقدرة التشغيلية.</p>
<p>بالنسبة لصاحب القرار، هذه ليست فقط مسألة تشغيلية بل مسألة ربحية. فكل دقيقة تستهلكها مهمة متكررة هي دقيقة لا تذهب إلى البيع، أو خدمة العملاء، أو متابعة الملفات الحساسة، أو قيادة النشاط. والخبر الجيد أن هذه الكلفة يمكن قياسها بسرعة، وغالباً يمكن خفضها بسرعة أيضاً عبر أتمتة ذكاء اصطناعي جيدة الاستهداف.</p>

<h2 id="structural-cost">1. ما الذي يحول بضع دقائق إلى تكلفة هيكلية</h2>
<p>المشكلة في المهام المتكررة أنها موزعة ومتناثرة. فهي لا تبدو كمشروع واضح، بل كعادة يومية. ومع ذلك فهي تخلق تكلفة هيكلية لثلاثة أسباب:</p>
<ul>
    <li><strong>تقطع التركيز</strong> وتزيد من تبديل السياق بين المهام؛</li>
    <li><strong>تطيل كل دورة عمل</strong> لأن كل ملف أو طلب ينتظر تدخلاً يدوياً إضافياً؛</li>
    <li><strong>تشغل موظفين مؤهلين</strong> في أعمال منخفضة القيمة.</li>
</ul>
<p>بمعنى آخر، حتى عندما لا يشعر أحد بأنه يخسر ساعة كاملة، تكون الشركة قد جمعت كل أسبوع عشرات الساعات التي لا تصنع هامشاً إضافياً ولا ميزة تنافسية.</p>

<h2 id="calculate-loss">2. طريقة بسيطة لحساب الخسارة الشهرية</h2>
<p>المعادلة الأساسية بسيطة: <strong>عدد الأشخاص المعنيين × الوقت المهدور يومياً × الكلفة الساعة المحملة × عدد أيام العمل</strong>.</p>
<p>لنأخذ حالة واقعية: <strong>12 موظفاً</strong> يخسر كل منهم <strong>35 دقيقة يومياً</strong> في مهام متكررة، مع كلفة محملة متوسطة قدرها <strong>29 يورو للساعة</strong> وعلى أساس <strong>220 يوم عمل</strong> في السنة. النتيجة تصل إلى <strong>44,660 يورو سنوياً</strong>، أي حوالي <strong>3,722 يورو شهرياً</strong>.</p>
<p>وهذا الحساب لا يشمل بعدُ إعادة العمل، أو التأخير، أو التكرار، أو الفرص التي يتم التعامل معها متأخراً. ولهذا السبب تتحول مشكلة تشغيلية تبدو بسيطة إلى مسألة هامش وربحية من منظور الإدارة.</p>

<h2 id="business-examples">3. أمثلة عملية حسب الأقسام</h2>
<h3>المبيعات والإدارة التجارية</h3>
<p>فريق من <strong>10 أشخاص</strong> يقضي <strong>30 دقيقة يومياً</strong> في إعادة إدخال المعلومات، أو تحديث نظام إدارة العملاء، أو إرسال متابعات موحدة، يجمّد بالفعل <strong>31,900 يورو سنوياً</strong> مع كلفة محملة قدرها <strong>29 يورو للساعة</strong>. وهذا وقت لا يذهب إلى التحويل التجاري أو متابعة الحسابات ذات الأولوية.</p>
<h3>دعم العملاء والعمليات</h3>
<p>في فريق من <strong>7 أشخاص</strong>، فإن تخصيص <strong>50 دقيقة يومياً</strong> لفرز الطلبات، أو نسخ الحالات، أو الإجابة عن الأسئلة المتكررة يمثل قرابة <strong>35,933 يورو سنوياً</strong> مع كلفة قدرها <strong>28 يورو للساعة</strong>. وتأتي الكلفة المالية هنا فوق تجربة عميل أبطأ.</p>
<h3>المالية والموارد البشرية</h3>
<p>جمع المستندات، والتحقق، والمطابقات، وتحديث الجداول، والمتابعات الداخلية تتراكم بسرعة. وبالنسبة إلى <strong>5 أشخاص</strong> يخسرون <strong>70 دقيقة يومياً</strong> مع كلفة <strong>34 يورو للساعة</strong>، تصل الفاتورة إلى <strong>43,633 يورو سنوياً</strong>. وفي هذه الوظائف تقلل الأتمتة من الوقت الضائع ومن خطر الخطأ معاً.</p>

<h2 id="real-cost">4. لماذا تتجاوز الكلفة الحقيقية بند الرواتب</h2>
<p>الكلفة الظاهرة هي وقت العمل المهدور. أما الكلفة الحقيقية فتتجاوز ذلك:</p>
<ul>
    <li><strong>الأخطاء وإعادة الإدخال</strong> تزيد زمن المعالجة أكثر فأكثر؛</li>
    <li><strong>بطء الاستجابة</strong> يضعف رضا العملاء وجودة الخدمة؛</li>
    <li><strong>ضياع الفرص التجارية</strong> يضغط على الإيرادات عندما تتأخر العروض أو المتابعات؛</li>
    <li><strong>الإرهاق التشغيلي</strong> يقلل التركيز على الأعمال الأعلى قيمة.</li>
</ul>
<p>عملياً، الشركة لا تدفع فقط ثمن دقائق ضائعة، بل تدفع أيضاً ثمن تنظيم أبطأ وأكثر هشاشة وأقل قابلية للتوسع.</p>

<h2 id="where-to-start">5. أين تبدأ الأتمتة لاستعادة الهامش</h2>
<p>أفضل مشاريع أتمتة الذكاء الاصطناعي لا تبدأ عادةً بأكثر الحالات إبهاراً، بل تبدأ بالتسلسلات التي تتكرر كل يوم، وتتبع قواعد مستقرة، وتنقل البيانات بين الأدوات. عملياً، تكون الأولويات الأولى غالباً:</p>
<ul>
    <li>تأهيل الطلبات الواردة؛</li>
    <li>جمع المستندات والتحقق منها؛</li>
    <li>تحديث أنظمة CRM وERP أو جداول المتابعة الداخلية؛</li>
    <li>الردود الموحدة والمتابعات البسيطة؛</li>
    <li>إعداد الملخصات والتقارير الدورية.</li>
</ul>
<p>عندما يقرأ الذكاء الاصطناعي المعلومات ويصنفها ويجهزها ويتابعها أو يحدّثها تلقائياً، تحتفظ فرقك بالتحقق النهائي لكنها تستعيد ساعات مفيدة كل أسبوع. وهكذا يمكن استيعاب نشاط أكبر من دون توظيف مبكر، مع تحسين سرعة التنفيذ والهامش في الوقت نفسه.</p>
<p>إذا أردت تحديد المهام المتكررة التي تؤثر أكثر من غيرها في ربحية شركتك، تستطيع ZamanIA إجراء تدقيق سريع وعملي لتدفقات العمل لديك. راسلنا على <strong>contact@zamania.fr</strong> لحساب المكاسب المحتملة وترتيب أولويات الأتمتة الأعلى عائداً على الاستثمار.</p>
""".strip(),
    'card_fr': {
        'title': 'Le coût caché des tâches répétitives : la fuite silencieuse de marge dans votre entreprise',
        'date': '1 Juin 2026',
        'description': "Calculez la fuite silencieuse de marge créée par les micro-tâches répétitives et découvrez où l'automatisation IA peut avoir l'impact le plus rapide.",
        'cta': "Lire l'article",
        'image_url': f'../images/blog/{IMAGE_NAME}',
        'href': f'{SLUG}.html',
    },
    'card_en': {
        'title': 'The Hidden Cost of Repetitive Tasks: The Silent Margin Drain in Your Business',
        'date': 'June 1, 2026',
        'description': 'Measure the silent margin drain caused by repetitive micro-tasks and see where AI automation can deliver the fastest impact.',
        'cta': 'Read article',
        'image_url': f'../../images/blog/{IMAGE_NAME}',
        'href': f'{SLUG}.html',
    },
    'card_ar': {
        'title': 'التكلفة الخفية للمهام المتكررة: النزيف الصامت لهامش الربح في شركتك',
        'date': '1 يونيو 2026',
        'description': 'قِس النزيف الصامت لهامش الربح الناتج عن المهام الصغيرة المتكررة واكتشف أين تمنح أتمتة الذكاء الاصطناعي أسرع أثر.',
        'cta': 'اقرأ المقال',
        'image_url': f'../../images/blog/{IMAGE_NAME}',
        'href': f'{SLUG}.html',
    },
}


def find_choice() -> tuple[str, str, bool, dict | None]:
    selection_payload = None
    if SELECTION_PATH.exists():
        selection_payload = json.loads(SELECTION_PATH.read_text(encoding='utf-8'))
        status = selection_payload.get('status')
        choice = str(selection_payload.get('choice')) if selection_payload.get('choice') is not None else None
        if status == 'pending' and choice in {'1', '2', '3'}:
            return choice, 'selection_file', True, selection_payload

    if SESSIONS_INDEX_PATH.exists():
        sessions_index = json.loads(SESSIONS_INDEX_PATH.read_text(encoding='utf-8'))
        target_entry = None
        for value in sessions_index.values():
            origin = value.get('origin', {})
            if value.get('platform') == 'telegram' and value.get('chat_type') == 'dm' and str(origin.get('chat_id')) == TELEGRAM_CHAT_ID:
                target_entry = value
                break
        if target_entry:
            session_path = Path(f"/opt/data/sessions/session_{target_entry['session_id']}.json")
            if session_path.exists():
                session_data = json.loads(session_path.read_text(encoding='utf-8'))
                messages = session_data.get('messages', [])
                session_day = (session_data.get('last_updated') or target_entry.get('updated_at') or '')[:10]
                if session_day == TODAY_ISO_DATE:
                    today_messages: list[dict] = []
                    for msg in messages:
                        timestamp = None
                        for key in ('timestamp', 'created_at', 'time', 'date'):
                            value = msg.get(key)
                            if isinstance(value, str) and len(value) >= 10:
                                timestamp = value[:10]
                                break
                        if timestamp is None or timestamp == TODAY_ISO_DATE:
                            today_messages.append(msg)
                    marker_seen = False
                    last_user_choice = None
                    for msg in today_messages:
                        content = (msg.get('content') or '').strip()
                        if msg.get('role') == 'assistant' and content == MARKER:
                            marker_seen = True
                            last_user_choice = None
                            continue
                        if marker_seen and msg.get('role') == 'user' and content in {'1', '2', '3'}:
                            last_user_choice = content
                    if last_user_choice:
                        return last_user_choice, 'telegram', False, selection_payload

    return '1', 'default', False, selection_payload


def render_sommaire(items: list[tuple[str, str]]) -> str:
    return '\n'.join([f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in items])


def render_page(template_path: Path, title: str, date_label: str, description: str, sommaire_html: str, content_html: str, image_url: str) -> str:
    template = template_path.read_text(encoding='utf-8')
    return (
        template
        .replace('{{TITLE}}', title)
        .replace('{{DATE}}', date_label)
        .replace('{{DESCRIPTION}}', description)
        .replace('{{SOMMAIRE}}', sommaire_html)
        .replace('{{CONTENT}}', content_html)
        .replace('{{IMAGE_URL}}', image_url)
    )


def build_card(card: dict) -> str:
    return f"""
            <article class="blog-card">
                <img src="{card['image_url']}" alt="{card['title']}">
                <div class="blog-card-content">
                    <span class="blog-card-date">{card['date']}</span>
                    <h3>{card['title']}</h3>
                    <p>{card['description']}</p>
                    <a href="{card['href']}">{card['cta']}</a>
                </div>
            </article>
""".rstrip()


def insert_card(index_path: Path, card_html: str) -> None:
    text = index_path.read_text(encoding='utf-8')
    if f'{SLUG}.html' in text:
        return
    replacement = MARKER_HTML + '\n\n' + card_html + '\n'
    updated = text.replace(MARKER_HTML, replacement, 1)
    index_path.write_text(updated, encoding='utf-8')


def clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))


def alpha_blend(pixels: bytearray, width: int, x: int, y: int, color: tuple[int, int, int], alpha: float) -> None:
    if not (0 <= x < width):
        return
    height = len(pixels) // (width * 3)
    if not (0 <= y < height):
        return
    idx = (y * width + x) * 3
    inv = 1.0 - alpha
    pixels[idx] = clamp(pixels[idx] * inv + color[0] * alpha)
    pixels[idx + 1] = clamp(pixels[idx + 1] * inv + color[1] * alpha)
    pixels[idx + 2] = clamp(pixels[idx + 2] * inv + color[2] * alpha)


def blend_rect(pixels: bytearray, width: int, x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int], alpha: float) -> None:
    height = len(pixels) // (width * 3)
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)
    for y in range(y1, y2):
        row = (y * width + x1) * 3
        for x in range(x1, x2):
            inv = 1.0 - alpha
            pixels[row] = clamp(pixels[row] * inv + color[0] * alpha)
            pixels[row + 1] = clamp(pixels[row + 1] * inv + color[1] * alpha)
            pixels[row + 2] = clamp(pixels[row + 2] * inv + color[2] * alpha)
            row += 3


def draw_line(pixels: bytearray, width: int, x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int], thickness: int = 2, alpha: float = 1.0) -> None:
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy), 1)
    for step in range(steps + 1):
        t = step / steps
        x = int(round(x1 + dx * t))
        y = int(round(y1 + dy * t))
        for oy in range(-thickness, thickness + 1):
            for ox in range(-thickness, thickness + 1):
                if ox * ox + oy * oy <= thickness * thickness:
                    alpha_blend(pixels, width, x + ox, y + oy, color, alpha)


def draw_circle(pixels: bytearray, width: int, cx: int, cy: int, radius: int, color: tuple[int, int, int], alpha: float = 1.0) -> None:
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                alpha_blend(pixels, width, x, y, color, alpha)


def create_image(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 900
    pixels = bytearray(width * height * 3)
    glow_points = [
        (1180, 170, 240, (0, 240, 255), 0.55),
        (420, 720, 300, (107, 91, 255), 0.40),
        (980, 520, 220, (0, 190, 255), 0.30),
    ]

    for y in range(height):
        fy = y / (height - 1)
        for x in range(width):
            fx = x / (width - 1)
            r = 10 + 10 * fx + 8 * fy
            g = 18 + 26 * fx + 16 * fy
            b = 34 + 52 * fx + 32 * fy

            band = math.exp(-((fy - (0.78 - 0.46 * fx)) / 0.17) ** 2)
            r += 8 * band
            g += 42 * band
            b += 65 * band

            wave = (math.sin(fx * 11.0 + fy * 7.0) + 1.0) / 2.0
            r += 4 * wave
            g += 6 * wave
            b += 8 * wave

            for cx, cy, sigma, color, intensity in glow_points:
                dist2 = (x - cx) ** 2 + (y - cy) ** 2
                glow = math.exp(-dist2 / (2 * sigma * sigma)) * intensity
                r += color[0] * glow
                g += color[1] * glow
                b += color[2] * glow

            if x % 100 == 0 or y % 100 == 0:
                r += 3
                g += 5
                b += 7

            idx = (y * width + x) * 3
            pixels[idx] = clamp(r)
            pixels[idx + 1] = clamp(g)
            pixels[idx + 2] = clamp(b)

    blend_rect(pixels, width, 110, 120, 640, 340, (12, 22, 34), 0.55)
    blend_rect(pixels, width, 980, 130, 1490, 390, (12, 24, 38), 0.52)
    blend_rect(pixels, width, 310, 530, 1280, 790, (8, 18, 30), 0.42)

    for x in range(180, 610, 75):
        draw_line(pixels, width, x, 300, x, 155, (0, 230, 255), 3, 0.92)
    for y in range(160, 301, 35):
        draw_line(pixels, width, 165, y, 610, y, (80, 115, 150), 1, 0.65)

    bar_heights = [55, 85, 125, 95, 150]
    bar_x = 220
    for h in bar_heights:
        blend_rect(pixels, width, bar_x, 300 - h, bar_x + 42, 300, (0, 240, 255), 0.88)
        bar_x += 68

    draw_line(pixels, width, 1040, 340, 1130, 300, (250, 190, 50), 3, 0.95)
    draw_line(pixels, width, 1130, 300, 1220, 250, (250, 190, 50), 3, 0.95)
    draw_line(pixels, width, 1220, 250, 1310, 275, (250, 190, 50), 3, 0.95)
    draw_line(pixels, width, 1310, 275, 1400, 200, (250, 190, 50), 3, 0.95)
    for point in [(1040, 340), (1130, 300), (1220, 250), (1310, 275), (1400, 200)]:
        draw_circle(pixels, width, point[0], point[1], 8, (255, 210, 90), 0.98)

    draw_line(pixels, width, 420, 700, 590, 610, (0, 225, 255), 4, 0.85)
    draw_line(pixels, width, 590, 610, 770, 640, (107, 91, 255), 4, 0.85)
    draw_line(pixels, width, 770, 640, 980, 560, (0, 225, 255), 4, 0.85)
    draw_line(pixels, width, 980, 560, 1170, 600, (107, 91, 255), 4, 0.85)
    for point, color in [((420, 700), (0, 225, 255)), ((590, 610), (107, 91, 255)), ((770, 640), (0, 225, 255)), ((980, 560), (107, 91, 255)), ((1170, 600), (0, 225, 255))]:
        draw_circle(pixels, width, point[0], point[1], 10, color, 0.95)

    with tempfile.TemporaryDirectory() as tmpdir:
        ppm_path = Path(tmpdir) / 'zamania-blog-art.ppm'
        with ppm_path.open('wb') as fh:
            fh.write(f'P6\n{width} {height}\n255\n'.encode('ascii'))
            fh.write(pixels)
        subprocess.run([
            'ffmpeg', '-y', '-loglevel', 'error', '-i', str(ppm_path), '-q:v', '2', str(output_path)
        ], check=True)


def maybe_update_selection(selection_payload: dict | None, used_selection: bool, links: dict[str, str]) -> None:
    if not used_selection or selection_payload is None:
        return
    selection_payload['status'] = 'published'
    selection_payload['published_at'] = TODAY.replace(microsecond=0).isoformat()
    selection_payload['slug'] = SLUG
    selection_payload['links'] = links
    SELECTION_PATH.write_text(json.dumps(selection_payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    choice, choice_source, used_selection, selection_payload = find_choice()
    if choice != '1':
        choice = '1'
        choice_source = f'{choice_source}_fallback_to_topic_1'

    fr_page = render_page(
        BASE / 'blog' / 'template.html',
        ARTICLE['title_fr'],
        ARTICLE['date_fr'],
        ARTICLE['description_fr'],
        render_sommaire(ARTICLE['sommaire_fr']),
        ARTICLE['content_fr'],
        f'../images/blog/{IMAGE_NAME}',
    )
    en_page = render_page(
        BASE / 'en' / 'blog' / 'template.html',
        ARTICLE['title_en'],
        ARTICLE['date_en'],
        ARTICLE['description_en'],
        render_sommaire(ARTICLE['sommaire_en']),
        ARTICLE['content_en'],
        f'../../images/blog/{IMAGE_NAME}',
    )
    ar_page = render_page(
        BASE / 'ar' / 'blog' / 'template.html',
        ARTICLE['title_ar'],
        ARTICLE['date_ar'],
        ARTICLE['description_ar'],
        render_sommaire(ARTICLE['sommaire_ar']),
        ARTICLE['content_ar'],
        f'../../images/blog/{IMAGE_NAME}',
    )

    (BASE / 'blog' / f'{SLUG}.html').write_text(fr_page, encoding='utf-8')
    (BASE / 'en' / 'blog' / f'{SLUG}.html').write_text(en_page, encoding='utf-8')
    (BASE / 'ar' / 'blog' / f'{SLUG}.html').write_text(ar_page, encoding='utf-8')

    insert_card(BASE / 'blog' / 'index.html', build_card(ARTICLE['card_fr']))
    insert_card(BASE / 'en' / 'blog' / 'index.html', build_card(ARTICLE['card_en']))
    insert_card(BASE / 'ar' / 'blog' / 'index.html', build_card(ARTICLE['card_ar']))

    create_image(IMAGE_PATH)

    links = {
        'fr': f'https://zamania.fr/blog/{SLUG}.html',
        'en': f'https://zamania.fr/en/blog/{SLUG}.html',
        'ar': f'https://zamania.fr/ar/blog/{SLUG}.html',
    }
    maybe_update_selection(selection_payload, used_selection, links)

    result = {
        'published_subject': ARTICLE['subject_fr'],
        'published_title_fr': ARTICLE['title_fr'],
        'choice_used': choice if choice_source != 'default' else 'default',
        'raw_choice': choice,
        'choice_source': choice_source,
        'slug': SLUG,
        'image_path': str(IMAGE_PATH),
        'links': links,
        'selection_updated': used_selection,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
