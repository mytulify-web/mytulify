#!/usr/bin/env python3
"""Rewrite thin auto-generated tool guides into specific how-to articles.

Keeps the URL, title, and related tools. Replaces the repeated template body.
Skips posts that were written by hand.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "content" / "blog"
CATS = ROOT / "src" / "lib" / "catalog" / "categories"

TEMPLATE_A = "That is the whole scope of the page."
TEMPLATE_B = "only does the job in that first sentence."

OCR_LANGS = [
    "Arabic", "Bengali", "Chinese", "Dutch", "English", "French", "German", "Greek",
    "Gujarati", "Hindi", "Indonesian", "Italian", "Japanese", "Kannada", "Korean",
    "Malayalam", "Marathi", "Persian", "Polish", "Portuguese", "Punjabi", "Russian",
    "Spanish", "Swedish", "Tamil", "Telugu", "Thai", "Turkish", "Ukrainian", "Vietnamese",
]

LANG_NOTE = {
    "Arabic": "Arabic is written right to left. Dots separate letters that share a skeleton, and short vowels are often left out. Check those dots against the photo before you translate.",
    "Bengali": "Bengali letters hang from a headline bar. A broken headline or a missing vowel sign changes the word. Compare the headline, not only the loops.",
    "Chinese": "Chinese handwriting is characters, not an alphabet. A simplified and a traditional form of the same word are different characters. Confirm any character you do not already know.",
    "Dutch": "Dutch handwriting often joins ij and uses a long loop on the g and y. Read names twice; a capital can look like a lower-case letter.",
    "English": "English cursive joins letters, so u, n, and r blur together. Read the word, then the letters, and mark anything you guessed.",
    "French": "French handwriting uses accents. A missing accent changes the word, so check é, è, ê, and ç against the photo before you translate.",
    "German": "German handwriting may use ß and umlauts. The old Kurrent hand looks unlike modern print. Do not treat a guessed umlaut as confirmed.",
    "Greek": "Greek letters such as ν, υ, and ρ are easy to swap with Latin lookalikes. Keep the Greek output, and only then translate.",
    "Gujarati": "Gujarati has no headline bar. Vowel signs sit above, below, or before the consonant. A sign in the wrong place is a different syllable.",
    "Hindi": "Hindi uses Devanagari. The headline bar, the dot of the anusvara, and matras carry meaning. Check matras that sit before the consonant.",
    "Indonesian": "Indonesian uses the Latin alphabet with simple affixes. The risk is joined handwriting, not a special script. Read proper names letter by letter.",
    "Italian": "Italian handwriting keeps accents on the final vowel of many words. A missing accent can change both the meaning and the pronunciation.",
    "Japanese": "Japanese mixes kanji, hiragana, and katakana. A kanji guess that is only close is still the wrong word. Keep the original script beside the translation.",
    "Kannada": "Kannada letters are round, and vowel signs attach in several positions. Compare the sign, not only the round body of the letter.",
    "Korean": "Korean hangs syllables in blocks. A stroke that looks optional may be a different jamo. Read each block, then the word.",
    "Malayalam": "Malayalam letters are curly and often conjunct. A small loop changes the consonant. Zoom in before you accept a rare word.",
    "Marathi": "Marathi uses Devanagari with its own vocabulary. Do not assume a Hindi reading of a Marathi word just because the script matches.",
    "Persian": "Persian is right to left and uses a different set of letters from Arabic for p, ch, zh, and g. Those extra dots are the letters, not decoration.",
    "Polish": "Polish handwriting uses diacritics such as ł, ż, and ń. A stroke through an l is a different letter. Check names and place names.",
    "Portuguese": "Portuguese uses tildes and cedillas. ã and ç change the word. Confirm them on the photo before you translate into another language.",
    "Punjabi": "Punjabi in Gurmukhi hangs from a headline and uses a distinct set of letters. A pair of similar letters is often told apart by one dot or a foot.",
    "Russian": "Russian cursive looks very different from printed Cyrillic. т, ш, and м are common confusions. Read the whole word, then check each letter.",
    "Spanish": "Spanish handwriting uses ñ and accents. The tilde on ñ is not a stray mark. A missing accent can point at a different word.",
    "Swedish": "Swedish uses å, ä, and ö as separate letters. Dropping the ring or the dots changes the word, including names.",
    "Tamil": "Tamil vowels can appear as a sign before or after the consonant, and some letters look alike in a hurry. Check the vowel sign first.",
    "Telugu": "Telugu letters are round, with vowel marks that are easy to clip in a photo. If a loop is cut off, treat that syllable as unread.",
    "Thai": "Thai has no spaces between words, and vowels can sit above, below, before, or after a consonant. Do not insert spaces and then assume they were in the original.",
    "Turkish": "Turkish distinguishes ı and i, and also ö, ü, ş, ğ, and ç. The dot on the i is a different letter from the dotless ı.",
    "Ukrainian": "Ukrainian cursive is close to Russian but uses і, ї, є, and ґ. Those letters are not optional variants. Check them before you translate.",
    "Vietnamese": "Vietnamese is Latin script with many tone marks. A different tone is a different word. If a mark is faint, mark that syllable as uncertain.",
}


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def load_tools() -> dict[str, dict]:
    tools: dict[str, dict] = {}
    for path in CATS.glob("*.json"):
        data = json.loads(path.read_text())
        for tool in data["tools"]:
            key = f"{data['slug']}/{tool['slug']}"
            tools[key] = {
                **tool,
                "category": data["slug"],
                "categoryName": data["name"],
            }
    specials = [
        ("handwriting-to-text", "Handwriting to Text (OCR)", "Convert a photo of handwriting into digital text in any language, then optionally translate it."),
        ("handwritten-math-ocr", "Handwritten Math to LaTeX", "Photograph handwritten equations and get clean LaTeX, ASCII math, or a step-by-step solution."),
        ("handwritten-notes-summarizer", "Handwritten Notes Summarizer", "Upload handwritten notes and get a summary, outline, meeting minutes, or study flashcards."),
        ("handwritten-form-extractor", "Handwritten Form Extractor", "Pull filled fields from a handwritten form into JSON, CSV, or a Markdown table."),
        ("handwritten-table-ocr", "Handwritten Table OCR", "Turn a photo of a handwritten table or grid into Markdown, CSV, or JSON rows."),
        ("handwriting-to-markdown", "Handwriting to Markdown", "Convert a handwritten page into clean Markdown with headings and lists."),
    ]
    for slug, name, desc in specials:
        tools[f"handwriting-ocr/{slug}"] = {
            "slug": slug,
            "name": name,
            "description": desc,
            "category": "handwriting-ocr",
            "categoryName": "Handwriting OCR",
            "clientSide": False,
        }
    for lang in OCR_LANGS:
        slug = "handwriting-to-text-" + lang.lower().replace(" ", "-")
        tools[f"handwriting-ocr/{slug}"] = {
            "slug": slug,
            "name": f"{lang} Handwriting to Text",
            "description": f"Convert {lang} handwriting from a photo into editable {lang} text, with optional translation into another language.",
            "category": "handwriting-ocr",
            "categoryName": "Handwriting OCR",
            "clientSide": False,
            "language": lang,
        }
    return tools


def parse_frontmatter(raw: str) -> tuple[dict[str, str], list[str], str]:
    match = re.match(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$", raw)
    if not match:
        raise ValueError("missing frontmatter")
    data: dict[str, str] = {}
    related: list[str] = []
    in_related = False
    for line in match.group(1).splitlines():
        if in_related and re.match(r"^\s+-\s+", line):
            related.append(re.sub(r"^\s+-\s+", "", line).strip().strip("\"'"))
            continue
        in_related = False
        kv = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not kv:
            continue
        key, val = kv.group(1), kv.group(2).strip().strip("\"'")
        if key == "relatedToolSlugs":
            in_related = True
            continue
        data[key] = val
    return data, related, match.group(2)


def lower_first(text: str) -> str:
    text = text.strip().rstrip(".")
    if not text:
        return text
    return text[0].lower() + text[1:]


def explain(tool: dict) -> tuple[str, str, str, str]:
    slug = tool["slug"]
    name = tool["name"]
    desc = tool["description"].strip().rstrip(".")
    category = tool["category"]
    lang = tool.get("language")

    if lang:
        note = LANG_NOTE.get(lang, f"Read the {lang} output against the photo before you translate it.")
        return (
            f"Use a sharp photo where the {lang} writing fills the frame. Crop the desk, the fingers, and the glare. One page at a time is more reliable than a whole notebook in one shot.",
            f"Upload one page you can still read yourself. Keep the original {lang} text, then turn on translation only if you need a second language. {note}",
            "Put the photo and the text side by side. Check names, numbers, and any word you would quote. A gap or a [illegible] mark is a place to look again, not a word to invent.",
            f"{name} reads the handwriting in the photo. It does not verify that the note is true, and a translation can smooth over a word the model was unsure about.",
        )

    if slug == "handwriting-to-text":
        return (
            "Use one clear photo of the page. Say which language the writing is in if you know it, and pick a translation only when you need one.",
            "Start with a page you can already read, so you can see which words the model missed. Then try the page you actually need.",
            "Compare line breaks, names, and digits with the photo. Joined letters and faint marks are the usual misses.",
            "This is a transcription, not a fact check. The model only sees the picture you uploaded.",
        )

    if slug == "handwritten-math-ocr":
        return (
            "Photograph the equation so the symbols are large. Pick LaTeX if you will paste into a paper, ASCII if you will paste into chat, or the step mode if you want a worked solution.",
            "A simple case is a quadratic such as x squared minus 5x plus 6. The page should return the expression, and the step mode should solve it only if the photo shows a problem to solve.",
            "Compile the LaTeX or retype one symbol you are unsure about. A misread sign or a lost exponent changes the math.",
            "The solver works from the expression it read. If the reading is wrong, the steps are wrong too.",
        )

    if slug == "handwritten-notes-summarizer":
        return (
            "Upload the notes, then choose a summary, an outline, minutes, or flashcards. The choice changes the shape of the answer, not the photo.",
            "Use a one-page meeting note you remember. Check that the names and the decisions in the summary were actually on the page.",
            "A summary can drop a caveat that was in the margin. Read the photo for anything you would be embarrassed to lose.",
            "It does not know what happened off the page. It organizes the words it could read.",
        )

    if slug == "handwritten-form-extractor":
        return (
            "Photograph the filled form flat, with the labels visible. Choose JSON, CSV, or a Markdown table depending on where you will paste the fields.",
            "Try a form where you already know two answers, such as a name and a date. Those two fields tell you whether the columns landed in the right place.",
            "Match every value to its label. A shifted column is worse than a blank, because it looks finished.",
            "It extracts what was written. It does not check that the form was filled in correctly.",
        )

    if slug == "handwritten-table-ocr":
        return (
            "Photograph the grid so the lines are visible. Choose Markdown, CSV, or JSON for the tool that will open the table next.",
            "Use a small table, three columns by four rows, whose totals you can add by hand. If a number jumps a column, the total will not match.",
            "Open the CSV in a spreadsheet and check the header row. Merged cells in the photo often become repeated or empty cells.",
            "It does not invent rows that were outside the photo, and a stained grid line can split one cell into two.",
        )

    if slug == "handwriting-to-markdown":
        return (
            "Photograph a page that already has headings or a list. The tool is trying to keep that structure, not only the words.",
            "Use a page with one underlined heading and a few bullets. The heading should become a Markdown heading and the bullets should stay a list.",
            "Check heading levels and whether a list was flattened into a paragraph. Fix those before you publish the Markdown.",
            "It preserves wording. It does not add sections that were not on the page.",
        )

    if category == "calculators":
        return calculator_note(slug, name, desc)
    if category == "home-trade-calculators":
        return home_note(slug, name, desc)
    if category == "health-tools":
        return health_note(slug, name, desc)
    if category == "image-tools":
        return image_note(slug, name, desc)
    if category == "pdf-tools":
        return pdf_note(slug, name, desc)
    if category == "unit-converters":
        return unit_note(slug, name, desc)
    if category == "color-tools":
        return color_note(slug, name, desc)
    if category == "text-tools":
        return text_note(slug, name, desc)
    if category == "developer-tools" or category == "devops-tools" or category == "converters-generators":
        return dev_note(slug, name, desc)
    if category == "security-password-tools":
        return security_note(slug, name, desc)
    if category == "seo-web-tools":
        return seo_note(slug, name, desc)
    if category == "social-media-tools":
        return social_note(slug, name, desc)
    if category == "freelancer-tools":
        return freelance_note(slug, name, desc)
    if category == "ai-tools" or category == "content-creator-tools":
        return ai_note(slug, name, desc)
    return generic_note(name, desc)


def calculator_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    facts = {
        "bmi-calculator": (
            "Enter height and weight in one system. Do not mix centimetres with pounds.",
            "At 170 cm and 70 kg, BMI is weight divided by height in metres squared: 70 / 1.70² is about 24.2. The usual adult screening bands are under 18.5, 18.5–24.9, 25–29.9, and 30 or above.",
            "Change the height by one centimetre and watch the number move. A height error shifts BMI more than a small weight error.",
            "BMI does not measure body fat or fitness. Muscle, age, and pregnancy change what the same number means. It is not a diagnosis.",
        ),
        "percentage-calculator": (
            "Know which question you are asking: what is X percent of Y, what percent X is of Y, or the percent change from A to B.",
            "15% of 80 is 12. From 80 to 92 is a rise of 12, which is 12 / 80 = 15%. Those are different buttons, not the same sum.",
            "Say the question out loud before you read the answer. A percent change uses the starting number as the base.",
            "It does not know which number is the base unless you put it in the field that asks for the base.",
        ),
        "age-calculator": (
            "Use the date of birth and the date you want the age on. The second date is often today, but it does not have to be.",
            "Someone born on 23 October 2000 is 25 years and 0 days on 23 October 2025, and 24 years the day before. The tool counts years, then the leftover months and days.",
            "Check a birthday you know, including a leap-day birthday, before you trust a legal age.",
            "It counts calendar time. It does not apply a legal rule about when a person 'turns' an age in a particular country.",
        ),
        "loan-calculator": (
            "You need the amount borrowed, the annual interest rate, and the number of payments. Extra payments are optional.",
            "A standard amortizing loan pays interest on the remaining balance. Early payments are mostly interest. Later payments are mostly principal. The monthly payment stays flat if the rate and the term stay flat.",
            "Multiply the payment by the number of months and subtract the amount borrowed. That gap is the total interest. Compare it with the figure on the page.",
            "It does not include fees, insurance, or a rate that changes halfway through, unless the form has a field for them.",
        ),
        "mortgage-calculator": (
            "Principal and interest come from the loan amount, rate, and term. Taxes, insurance, HOA, and PMI are added on top. PMI usually applies when the down payment is under 20%.",
            "The same house costs more per month on a 15-year loan and less in total interest. A 30-year loan lowers the payment and raises the interest you pay over the life of the loan.",
            "Change only the term, from 30 years to 15, and read both the payment and the total interest. Then put taxes back in so you are looking at PITI, not only principal and interest.",
            "A lender's annual percentage rate, points, and mortgage insurance quote can differ from this estimate. This page does not pull your credit score.",
        ),
        "compound-interest-calculator": (
            "Enter the starting amount, the annual rate, the years, how often it compounds, and any regular contribution.",
            "Compounding means the interest itself earns interest. Monthly compounding at the same stated annual rate finishes slightly higher than annual compounding. A monthly contribution matters more than people expect because each deposit has less time to grow.",
            "Run it once with no contribution and once with the contribution. The gap is the deposits plus the growth on those deposits, not a higher rate.",
            "The rate you type is an assumption. A bank or a fund can change the rate, and this page does not subtract taxes or fees.",
        ),
        "tip-calculator": (
            "Enter the bill, the tip percent, and how many people are splitting it.",
            "On an 84 bill, 15% is 12.60, so the total is 96.60. Split by 3, each person owes 32.20 before any extra rounding.",
            "Check whether tax is already inside the bill you typed. Tipping on tax or on the pre-tax amount is a choice the form should make obvious.",
            "It splits the number you entered. It does not know who ordered what.",
        ),
        "discount-calculator": (
            "Enter the original price and the discount percent. If the store stacks two discounts, run it twice rather than adding the percents.",
            "20% off 50 is 10 off, so the sale price is 40. A second 10% off is 10% of 40, which is 4, not 10% of 50. The sale price is then 36, not 35.",
            "Read the amount saved and the sale price as a pair. They should add back to the original price.",
            "It does not apply a store rule such as 'discount taken before tax' unless you type the price at the stage you mean.",
        ),
        "sales-tax-calculator": (
            "Know whether you are adding tax onto a net price or pulling tax out of a price that already includes it. Those are different operations.",
            "At 8% tax, a 25 item becomes 27. If 27 already includes 8% tax, the net price is 27 / 1.08, which is 25, and the tax inside it is 2.",
            "The gross price should equal net plus tax. If it does not, you used the add mode when you needed the extract mode.",
            "Tax rates and what they apply to depend on the place and the product. The page uses the rate you type.",
        ),
        "calorie-calculator": (
            "The estimate starts from age, sex, height, weight, and an activity level, then a goal to maintain, lose, or gain.",
            "Maintenance is the calories that hold your current weight at the activity you selected. A loss target is a deficit from that number. A 500 kcal daily deficit is about a pound a week only as a rough energy rule, and bodies do not obey it exactly.",
            "Change only the activity level and see the maintenance calories move. If you picked 'athlete' for a desk job, the target is too high.",
            "This is not a meal plan and it does not know medical conditions, pregnancy, or the calories you actually eat.",
        ),
        "bmr-calculator": (
            "BMR is the energy a body uses at rest. The form needs weight, height, age, and sex because the common equations use those inputs.",
            "BMR is lower than the calories you should eat, because eating, walking, and working add activity on top. Use a TDEE page if you want the daily total.",
            "Compare the BMR with a TDEE result for the same body. TDEE should be higher once activity is included.",
            "Equations such as Mifflin-St Jeor are estimates. They are not a metabolic test.",
        ),
        "tdee-calculator": (
            "TDEE multiplies a resting burn by an activity factor. You need the body measurements and an honest activity level.",
            "A sedentary factor is close to 1.2 times BMR. A hard training day is higher. Picking the highest factor for a mostly seated week overstates the calories you use.",
            "The activity description on the form should match your week, not your best week. Read the factor you selected before you copy the calories.",
            "It does not count a single workout. A calories-burned page is the tool for one activity.",
        ),
        "body-fat-calculator": (
            "The US Navy method uses height, neck, and waist, plus hip for women. Measure in the units the label names, without pulling the tape tight.",
            "A smaller waist or a larger neck lowers the estimate for men. Measure at the same time of day if you are comparing two weeks, because food and water move the waist.",
            "Repeat the waist measurement once. If the two tapes differ by more than about a centimetre, the body-fat number will move with them.",
            "This is not a DEXA scan. It is a circumference estimate.",
        ),
        "ideal-weight-calculator": (
            "Enter height, and age or sex if the form asks. Different formulas, such as Devine or Hamwi, do not return the same weight.",
            "Read the range, not a single target. A healthy range is wider than one 'ideal' kilo.",
            "If two formulas are shown, the gap between them is the uncertainty. Do not treat the lower number as a goal by itself.",
            "It does not know muscle, frame, or a clinician's target.",
        ),
        "due-date-calculator": (
            "Use the first day of the last menstrual period and the cycle length the form assumes, often 28 days.",
            "Naegele's rule adds 280 days, which is 40 weeks, to that last-period date when the cycle is 28 days. A longer cycle shifts the date later.",
            "Count 40 weeks on a calendar from a date you know and compare. An ultrasound date from a clinic overrides this estimate.",
            "It is not a medical diagnosis of the due date. A clinic may date the pregnancy from a scan.",
        ),
        "ovulation-calculator": (
            "Enter the first day of the last period and the usual cycle length. Ovulation is estimated about 14 days before the next period, not 14 days after day one, when the cycle is not 28 days.",
            "On a 30-day cycle, the next period is about day 31 and ovulation is about day 16. The fertile window is the days leading up to that, because sperm live longer than the egg.",
            "If your cycles vary by more than a few days, the window is a guess. Compare two cycle lengths in the form and see the date move.",
            "It does not detect ovulation. A test strip or a clinician does that.",
        ),
        "pregnancy-calculator": (
            "Enter the dating input the form asks for, usually the last period or a known due date, and read the week it returns.",
            "Pregnancy is counted in completed weeks. Week 12 and '12 weeks and 6 days' are not the same day. Milestones on the page are tied to that week count.",
            "Check the week against a due date 40 weeks from the last period. If those two disagree, one of the inputs is not the date you think it is.",
            "It does not replace prenatal care, and it does not know the dating scan.",
        ),
        "gpa-calculator": (
            "Each course needs a grade and a number of credits. GPA is credit-weighted: a 4-credit A moves the average more than a 1-credit A.",
            "On a 4.0 scale, an A in 3 credits and a C in 3 credits is (4×3 + 2×3) / 6 = 3.0. An unweighted mean of the letters would be the same only because the credits matched.",
            "Add the quality points yourself for two courses. If your school uses plus and minus grades, use the points your school publishes, not a guessed 4.0.",
            "Schools do not share one scale. A 4.0, a 10-point scale, and a percentage scale are different tools settings.",
        ),
        "grade-calculator": (
            "Enter the weights and the scores you already have, and the weight of the exam you have not taken yet.",
            "If homework is 40% and you have 90, and the final is 60%, the score you need on the final depends on the course grade you want. A target of 80 requires the weighted sum of both parts to equal 80.",
            "The weights on the form should add to 100%. If they do not, the 'score you need' is answering a different course than yours.",
            "It applies the weights you type. It does not know dropped quizzes or extra credit unless you include them.",
        ),
        "fraction-calculator": (
            "Enter the numerators and denominators, and the operation. Mixed numbers should be converted to improper fractions if the form does not have a mixed-number field.",
            "1/2 + 1/3 is 3/6 + 2/6 = 5/6. The page should reduce the result. 2/4 should become 1/2.",
            "Multiply the result by the denominator and see if you land on the numerator. That catches a reduction error.",
            "It does not work in decimals unless you convert. A decimal approximation and an exact fraction are different answers.",
        ),
        "scientific-calculator": (
            "Use the degree or radian mode that matches the problem. Sine of 90 degrees is 1. Sine of 90 radians is not.",
            "Type a problem you know, such as the square root of 144, or 2 raised to the 10th, before you trust a longer expression. Parentheses change the order of operations.",
            "Watch the mode indicator. A wrong angle mode is the most common reason a correct-looking expression is wrong.",
            "It calculates what you type. It does not know which formula the homework asked for.",
        ),
        "date-calculator": (
            "Decide whether you are adding days to a date or counting the days between two dates. Include or exclude the end date the way your contract does.",
            "From 1 March to 1 April is 31 days of span if you count the distance, and the landing date after adding 31 days to 1 March is 1 April in a non-leap March. February's length depends on the year.",
            "Test a leap day. 2024 is a leap year. 1900 is not. The result should follow the calendar, not a 365-day assumption, when you cross February.",
            "Business-day rules, holidays, and 'end of the month' clauses are not in the calendar math unless the form says they are.",
        ),
        "hours-calculator": (
            "Enter the start and end times. If a shift crosses midnight, the end time is on the next day.",
            "08:00 to 17:30 is 9 hours and 30 minutes, which is 9.5 hours if you are writing a timesheet in decimals. 30 minutes is 0.5, not 0.3.",
            "Add the decimal hours for a week and compare with the hours-and-minutes total. A 0.3 versus 0.5 mistake shows up on payday.",
            "It does not subtract an unpaid lunch unless there is a break field and you fill it in.",
        ),
        "time-duration-calculator": (
            "Enter both date-times, not only the clock times, when the span crosses midnight or a month.",
            "From 22:00 on one day to 06:00 the next day is 8 hours. The same clock times on one day would be negative or nonsense if the form requires the end to be later.",
            "Read the result in hours and in days. A 36-hour span is 1 day and 12 hours, not 1.36 days.",
            "Time zones are part of the input if the two stamps are from different zones. This page uses the times you type.",
        ),
        "countdown-calculator": (
            "Enter the target date and time, and notice whether the clock is counting in your local time.",
            "A target of tomorrow at 09:00 should show a little under or over 24 hours depending on what time it is now. Days, hours, and minutes should agree with that.",
            "Refresh and see the minutes drop. If the date is in the past, the page should show that the moment has passed rather than a confusing negative.",
            "It does not include travel time or a reminder. It only measures the gap.",
        ),
        "paycheck-calculator": (
            "Enter gross pay, how often you are paid, and the deductions the form lists. A result is only as complete as the deductions you included.",
            "Take-home is gross minus taxes and other deductions. A pre-tax retirement contribution lowers the taxable pay on a real paycheck. If the form has no field for that, do not assume it was subtracted.",
            "Compare one period with the yearly figure. Monthly times 12, or weekly times 52, should land near the annual take-home the page shows.",
            "Payroll rules differ by country and by benefits. This is a planning estimate, not a pay stub.",
        ),
        "salary-calculator": (
            "Enter one rate and the schedule you want to convert. Hourly to annual assumes a number of hours per week, often 40.",
            "20 per hour at 40 hours and 52 weeks is 41,600 a year, before tax. A 37.5-hour week is 39,000. The hours assumption is part of the answer.",
            "Divide the annual figure back by 52 and by the weekly hours. You should land on the hourly rate you started with.",
            "It converts rates. It does not compute tax, overtime law, or unpaid leave.",
        ),
        "sleep-calculator": (
            "Sleep cycles are often estimated at 90 minutes. The page suggests bedtimes or wake times a whole number of cycles away.",
            "If you need to wake at 06:30, counting back five cycles is 7 hours and 30 minutes, which points at 23:00, plus the minutes the form adds to fall asleep.",
            "Read the 'time to fall asleep' field. Ignoring it suggests a bedtime that is already too late.",
            "Cycles vary by person. This is not a sleep study, and it does not treat insomnia.",
        ),
        "random-number-generator": (
            "Set the lowest and highest number and how many results you want. Decide whether repeats are allowed.",
            "A roll of one number from 1 to 6 should never show 0 or 7. Ask for twenty numbers and scan for anything outside the range.",
            "If you need a draw without duplicates, turn repeats off and do not ask for more numbers than the range contains.",
            "Browser random numbers are fine for a game or a draw. They are not a cryptographic key.",
        ),
        "standard-deviation-calculator": (
            "Paste the data set. Know whether you want the sample standard deviation, which divides by n−1, or the population figure, which divides by n.",
            "The numbers 2, 4, and 6 have a mean of 4. The sample standard deviation is larger than the population one because the divisor is 2 instead of 3.",
            "Check the mean by hand. If the mean is wrong, the spread is wrong. Then confirm which divisor the page used.",
            "It describes the numbers you typed. It does not know if one of them was a typo or a different unit.",
        ),
        "zakat-calculator": (
            "Enter the gold, silver, cash, and other wealth the form asks for, in the units on the label. Nisab and the 2.5% rate depend on the values you enter.",
            "Zakat is commonly 2.5% of wealth above nisab that has been held for a lunar year. The page applies the rate and the nisab you are working with. It does not know your school of thought.",
            "Compute 2.5% of a round cash figure by hand and compare. Then check that gold was valued with the price you intended.",
            "This is a calculator, not a fatwa. Debts you owe and wealth that is exempt should be handled the way you have confirmed with someone qualified.",
        ),
        "afghan-date-converter": (
            "Enter a Solar Hijri date or a Gregorian date. The Afghan official calendar is Solar Hijri, also called Shamsi.",
            "Nowruz, the start of the Solar Hijri year, falls on the March equinox, around 20 or 21 March. A date in Hamal is the start of that year, not January.",
            "Convert a date forward and then back. You should land on the same day. If you do not, the day or the month number was off by one.",
            "Historical dates and regional observances can differ by a day at the new year. The page converts the calendar, not a local announcement.",
        ),
        "tasbih-counter": (
            "Tap once per remembrance. Set the target, often 33 or 100, if you want the counter to mark a completed round.",
            "Count a short round you can track, such as 10, and see that the number on the page matches your taps. A double tap from a sensitive screen is the usual miss.",
            "Reset before a new round so the next count does not include the last one.",
            "It counts taps. It does not recite for you, and it does not save a count after you close the page unless the page says it does.",
        ),
        "salary-tax-calculator": (
            "Enter gross pay and the country or the brackets the form uses. A tax estimate without the right brackets is a different country's tax.",
            "Tax is not a single percent of the whole salary when the system is progressive. The first slice is taxed at a lower rate than the next slice.",
            "Compare the tax plus the net with the gross. They should add up. If a deduction is pre-tax, it should shrink the taxable amount, not only the net.",
            "Allowances, credits, and local taxes change the real withholding. Use this to plan, then check a payslip or the tax office.",
        ),
        "emi-calculator": (
            "EMI is the fixed monthly payment on a reducing-balance loan. You need principal, annual interest rate, and tenure in months or years.",
            "Interest each month is the remaining principal times the monthly rate. The rest of the EMI reduces the principal. That is why the interest portion shrinks over time.",
            "The total you pay is EMI times the number of months. Subtract the principal to see total interest. A longer tenure lowers the EMI and raises that interest.",
            "Fees, insurance, and a floating rate are outside the EMI formula unless the form has fields for them.",
        ),
        "vat-gst-calculator": (
            "Choose add or extract, then type the rate. VAT and GST are calculated the same way here: a percent on top, or a percent inside a gross price.",
            "Adding 18% to 100 gives 118. Extracting 18% from 118 gives 100 of net and 18 of tax, because the gross is net times 1.18.",
            "If the net and the tax do not add to the gross, you are in the wrong mode.",
            "Which goods are taxed, and at which rate, is the law where you sell. The page uses the rate you type.",
        ),
        "profit-margin-calculator": (
            "Margin and markup are not the same. Margin is profit divided by the selling price. Markup is profit divided by the cost.",
            "Cost 60, price 100: profit is 40. Margin is 40/100 = 40%. Markup is 40/60 = 66.7%. A 40% markup on 60 is a price of 84, not 100.",
            "Read the label on the percent. If you wanted margin and the page shows markup, you will underprice.",
            "It ignores overhead you did not type: rent, tax, shipping, and payment fees.",
        ),
        "debt-payoff-calculator": (
            "List each debt with its balance, rate, and minimum. Snowball puts extra money on the smallest balance. Avalanche puts it on the highest rate.",
            "Avalanche usually pays less interest. Snowball clears a balance sooner, which is a behaviour difference, not a cheaper interest rate.",
            "Compare the total interest of the two plans with the same extra payment. The months and the interest should both be visible.",
            "A lender's minimum can change, and a promotional rate can expire. The schedule uses the rates you typed.",
        ),
        "inflation-calculator": (
            "Enter an amount, a start, an end, and an inflation rate. The page compounds that rate. It does not download a national price index unless it says so.",
            "At 6% a year, 100 today is about 100 × 1.06³ after three years, which is about 119. The same math backward tells you what 100 in the future is in today's money.",
            "A higher rate and a longer gap should both raise the future amount. If one of them does not, the fields are swapped.",
            "Your personal costs can rise faster or slower than the single rate you typed.",
        ),
        "sip-calculator": (
            "A SIP invests a fixed amount every month. You need the monthly amount, the expected annual return, and the years. Step-up means the monthly amount grows once a year.",
            "The future value of a monthly investment is not simply amount times months times the rate. Each instalment compounds for a different number of months. The first one grows the longest.",
            "Total invested should equal the monthly amount times the number of months, before any step-up. The maturity minus that invested figure is the estimated gain.",
            "The return you type is a hope, not a mutual-fund promise. The page does not subtract expense ratios or tax.",
        ),
        "cagr-calculator": (
            "CAGR needs a beginning value, an ending value, and the number of years. It is the steady annual rate that connects those two values.",
            "If 100 grows to 121 in two years, CAGR is the square root of 1.21, minus 1, which is 10% a year. The path can have gone down and back up. CAGR does not show that path.",
            "Beginning times (1 + CAGR) raised to the years should be close to the ending value.",
            "It is not the average of the yearly returns, and it is not XIRR. XIRR is for deposits on irregular dates.",
        ),
        "fd-calculator": (
            "A fixed deposit needs principal, annual rate, tenure, and how often interest compounds. Quarterly compounding earns a little more than annual compounding at the same stated rate.",
            "The maturity is principal times (1 + r/n) raised to n times years, where n is the number of compounds per year. Simple interest, if the form offers it, is principal times rate times time and does not compound.",
            "A higher compounding frequency should raise the maturity slightly. If it does not, the frequency control is not applied.",
            "Banks can quote rates before tax. This page does not withhold tax unless it has a tax field.",
        ),
        "ppf-calculator": (
            "PPF in India takes a yearly contribution, a rate, and a term up to the account rules you are using. Interest compounds yearly.",
            "Deposits are typically allowed for 15 years, and the balance keeps earning. The maturity on the page is contributions plus compounded interest at the rate you typed, not a rate locked by the government for the next 15 years.",
            "Total invested should match the yearly deposit times the years you entered. The rest of the maturity is interest.",
            "The notified PPF rate changes. Use the rate you want to plan with, and treat the result as a projection.",
        ),
        "swp-calculator": (
            "An SWP withdraws a fixed amount every month from a corpus that is also earning a return. You need the starting corpus, the withdrawal, the expected return, and the years.",
            "If the withdrawal is larger than the growth, the corpus falls and can hit zero before the years are up. The useful output is the remaining corpus and the month it would run out.",
            "Set the return to 0. The corpus should fall by exactly the withdrawals. That checks the arithmetic before you trust a growth assumption.",
            "Market returns are not a smooth yearly rate. This is a planning model.",
        ),
        "rd-calculator": (
            "A recurring deposit takes a monthly instalment, a rate, and a tenure. Quarterly compounding is the usual bank convention. Simple interest is a different, lower result.",
            "Each instalment earns interest for a different length of time. The first one earns the longest. Maturity is the instalments plus that interest, not instalment times months times the annual rate.",
            "Total deposited should equal the monthly amount times the number of months. Interest is maturity minus that sum.",
            "A bank's premature-closure penalty is not in the projection.",
        ),
        "lumpsum-calculator": (
            "A lumpsum is one amount invested once. You need that amount, the expected annual return, and the years.",
            "Future value is amount times (1 + rate) raised to the years, when compounding is annual. 100,000 at 10% for 3 years is 100,000 × 1.10³, which is 133,100.",
            "The gain should be the maturity minus the single amount you invested. There is no 'total invested' growth from monthly deposits on this page.",
            "It is not a SIP. Monthly investments belong on the SIP calculator.",
        ),
        "epf-calculator": (
            "EPF needs basic salary, the employee and employer contribution percents, the interest rate, and the years. In the common Indian setup the employee puts in 12% of basic, and part of the employer share goes to EPS rather than the EPF corpus.",
            "The corpus grows from contributions plus yearly interest. A higher basic raises the contribution. A higher rate raises the interest on the balance already there.",
            "Check one year by hand: contribution in, plus interest on the opening balance at the rate you typed. The page's first year should be in that neighbourhood.",
            "EPS wage caps and actual employer splits change. This is an estimate from the rates on the form, not a passbook.",
        ),
        "nps-calculator": (
            "NPS needs the monthly contribution, expected return, and years to retirement. The page may split the corpus into a lump sum and an annuity.",
            "The corpus is a compounded monthly investment at the return you hope for. The annuity portion is not cash you can spend on day one if the rules require you to buy an annuity with it.",
            "Look at the lump-sum percent separately from the corpus. A bigger corpus with a smaller withdrawable percent can still mean less cash in hand.",
            "NPS returns are market-linked. The rate on the form is not guaranteed, and annuity rates at retirement are unknown today.",
        ),
        "gratuity-calculator": (
            "The Payment of Gratuity Act formula commonly used in India is (15 × last drawn salary × years) / 26. A private or contractual formula often divides by 30 instead. Years often round up at a half year.",
            "Salary here usually means basic plus dearness allowance, not the whole CTC. Using CTC makes the gratuity too high.",
            "Compute 15/26 of one month of salary for one year of service and compare with the page. Then check whether your half year was rounded.",
            "Eligibility, the wage ceiling, and the tax exemption are legal questions. The page does the arithmetic you set up.",
        ),
        "hra-calculator": (
            "The usual Section 10(13A) exemption is the lowest of three numbers: actual HRA received, rent paid minus 10% of salary, and 50% of salary in a metro or 40% elsewhere.",
            "If rent is low, the 'rent minus 10% of salary' figure can be the smallest, and the exemption is that small number even if HRA received is large.",
            "Write down the three amounts and circle the smallest. The exemption on the page should be that circle, not the largest.",
            "Salary for this test is basic plus dearness allowance when those are the components the rule uses. City and rent receipts still have to be real.",
        ),
        "ssy-calculator": (
            "Sukanya Samriddhi Yojana takes a yearly deposit, typically for up to 15 years, and the account runs for 21 years from opening. The rate you type is compounded yearly.",
            "Deposits stop before the account does. The later years are interest on the balance, with no new deposit. The maturity should be higher than deposits times 15.",
            "Total invested should equal the yearly deposit times the deposit years, not times 21.",
            "The government notifies the rate. A projection at today's rate will not match a passbook if the rate changes.",
        ),
        "scss-calculator": (
            "SCSS takes a lump sum. Interest is paid out quarterly, and the principal comes back at the end of the tenure. You do not compound the interest if you withdraw it each quarter.",
            "Quarterly interest is the annual rate divided by 4, times the deposit. A 1,000,000 deposit at 8% pays about 20,000 each quarter. The principal at maturity is still 1,000,000 if you took the interest out.",
            "Four quarters of interest should equal one year at the annual rate. If the page compounds instead, you have selected a different product.",
            "Age rules, the investment cap, and tax on the interest are outside the interest arithmetic.",
        ),
        "nsc-calculator": (
            "NSC takes a lump sum, a notified rate, and a tenure, commonly five years, with annual compounding. Interest is not paid out each year. It stays inside the certificate.",
            "Maturity is principal times (1 + rate) raised to the years. You do not add a simple-interest coupon on the side.",
            "The gain is maturity minus the lump sum. That gain is the compounded interest, which is more than rate times years times principal.",
            "The notified rate for a new certificate can differ from an old one. Use the rate for the certificate you are buying.",
        ),
        "roi-calculator": (
            "ROI percent is the gain divided by the cost. Annualized ROI spreads that percent over the holding period so a two-year gain is not compared with a one-year gain as if they were the same.",
            "Cost 200, final value 250: net profit is 50 and ROI is 25%. Over two years, the annualized figure is lower than 25% because the 25% took two years.",
            "Profit plus cost should equal the final value. If it does not, cost and gain were entered in the wrong fields.",
            "ROI ignores the timing of cash flows in the middle. Use XIRR when money went in on several dates.",
        ),
        "xirr-calculator": (
            "XIRR needs each cash flow with its date. Money you invest is negative. Money you receive is positive. The answer is the annual rate that sets the present value of those flows to zero.",
            "One investment of 100 today and one return of 121 exactly two years later is about 10% a year, close to CAGR. Add a second deposit in the middle and CAGR on the first and last amounts becomes the wrong tool.",
            "The last cash flow should be the value you could withdraw on that date, signed positive. Forgetting the sign makes the rate meaningless.",
            "It matches the Excel-style idea of XIRR. It does not know fees that were not typed as their own cash flows.",
        ),
        "concrete-calculator": (
            "A slab's volume is length times width times thickness, all in the same unit, then converted to cubic yards or cubic metres. A round column uses the area of the circle times the height.",
            "A 10 ft by 10 ft slab, 4 inches thick, is 10 × 10 × (4/12) = 33.3 cubic feet, which is about 1.23 cubic yards before waste. Add the waste percent before you buy.",
            "An 80 lb bag yields less volume than a 60 lb bag. The bag count should rise when you switch to the heavier bag size if the yield per bag is smaller, or fall if the form's yield says otherwise. Read the bag yield on the page.",
            "This is an order-of-magnitude buy list. It is not a structural specification.",
        ),
        "paint-calculator": (
            "Wall area is the perimeter times the height, minus doors and windows, times the number of coats. Coverage is the square feet one gallon can do, printed on the can.",
            "A 12 by 12 room with 8 ft walls has about 384 square feet of wall before openings. At 350 square feet per gallon and two coats, you need more than two gallons before you subtract the door.",
            "Ceilings are a separate area. If you paint the ceiling, add length times width once per coat. Do not use the wall area for the ceiling.",
            "Texture, dark colours, and a thirsty primer change coverage. The can's number beats a generic 350.",
        ),
        "gravel-calculator": (
            "Volume is area times depth. Cubic yards are that volume in feet divided by 27. Tons depend on how heavy the material is per yard. Gravel, sand, and mulch do not weigh the same.",
            "A 10 by 20 ft path, 3 inches deep, is 50 cubic feet, or about 1.85 cubic yards. At a density of 1.4 tons per yard that is roughly 2.6 tons, before a waste margin.",
            "Changing the material should change the tons even when the yards stay the same. If the tons do not move, the density did not change.",
            "Depth in inches typed into a feet field orders three times too much, or too little. Read the unit on the depth box.",
        ),
        "square-footage-calculator": (
            "Pick the shape. A rectangle is length times width. A circle is pi times radius squared. A triangle is base times height divided by 2. A trapezoid uses the average of the two parallel sides times the height.",
            "A 12 by 10 room is 120 square feet. The same floor in metres is 120 / 10.764, about 11.1 square metres. The radius of a circle is half the width, not the width.",
            "For an L-shaped room, split it into two rectangles and add them. One rectangle around the whole L counts space you do not have.",
            "It measures area. It does not add waste for tiles or the gap around an island.",
        ),
        "fuel-cost-calculator": (
            "You need distance, the fuel economy, the price per gallon or litre, and how many people are splitting the cost.",
            "A 300 mile trip at 30 MPG uses 10 gallons. At 4 per gallon the fuel is 40, and two people pay 20 each. A second car at 20 MPG uses 15 gallons and costs 60. The savings is 20.",
            "Switching MPG should change gallons in the opposite direction. Better economy means fewer gallons.",
            "It does not include tolls, food, or a detour. Economy on the highway is not the city's figure.",
        ),
        "credit-card-payoff-calculator": (
            "Enter the balance, the annual percentage rate, and the monthly payment. The payment must be more than the month's interest or the balance never falls.",
            "Interest this month is roughly balance times APR divided by 12. Anything you pay above that reduces the principal. An extra payment every month shortens the term and cuts the total interest by more than the extra amount, because later months accrue less.",
            "If the page says the debt never pays off, the payment is below the interest. Raise the payment until a month count appears.",
            "Promotional rates and new charges are not in a single-balance payoff.",
        ),
        "debt-to-income-calculator": (
            "Front-end DTI is housing cost divided by gross monthly income. Back-end DTI adds the other monthly debts.",
            "Income of 5,000 and housing of 1,500 is a 30% front-end ratio. Add a 400 car payment and back-end is 1,900 / 5,000 = 38%. Lenders often look at back-end, and many want it under a cap they set, commonly discussed around 43% or lower.",
            "Use gross income, before tax, unless the form says net. Net income makes the ratio look worse.",
            "The page does not approve a loan. A lender's cap and their definition of housing cost decide that.",
        ),
        "home-affordability-calculator": (
            "The limit usually comes from a payment you can carry. That payment has to cover principal, interest, taxes, insurance, and the debts you already have, from your gross income.",
            "A higher rate lowers the price you can afford at the same monthly payment. A larger down payment raises the price because the loan is smaller. Debts you already pay reduce the payment left for the house.",
            "Move only the interest rate and watch the max price. It should fall when the rate rises.",
            "This is not a pre-approval. Association fees, the actual tax bill, and the lender's ratio are still theirs.",
        ),
        "apr-calculator": (
            "The note rate is the interest on the balance. APR folds in upfront fees, so it is higher than the note rate when you pay points or origination charges.",
            "Two loans with the same note rate are not the same cost if one charges fees. The APR is the way to compare them. The monthly payment is still calculated from the note rate and the amount you actually borrow.",
            "With zero fees, APR should sit on top of the note rate. If it does not, a fee field still has a number in it.",
            "APR is a disclosure math result, not the rate that accrues on your statement. Your statement uses the note rate.",
        ),
    }
    if slug in facts:
        return facts[slug]
    return generic_note(name, desc)


def home_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    facts = {
        "btu-calculator": (
            "Measure the room in feet, note the ceiling height, and count people, windows, and whether a kitchen is in the room. Sun and insulation change the load.",
            "Cooling load is estimated from the room's volume and those extras, then expressed in BTU per hour and in tons. Twelve thousand BTU per hour is one ton.",
            "A bigger room or a higher ceiling should raise the BTU. If you only changed the sun exposure, the BTU should still move.",
            "This sizes a rough load. It is not a Manual J calculation, and it does not pick the brand of the air conditioner.",
        ),
        "ac-tonnage-calculator": (
            "Use the floor area, a sense of the insulation, and the climate. The page rounds up to the next half ton so you do not buy a unit that is slightly small.",
            "One ton is 12,000 BTU per hour. A half ton is 6,000. Rounding up means a 1.1 ton estimate becomes 1.5 tons on the recommendation, which is a buying step, not a change in the room.",
            "Compare the BTU before rounding with the tons after rounding. The tons should never be below the raw BTU divided by 12,000.",
            "Oversizing cools fast and may not remove humidity. A contractor's load calc still wins for a whole house.",
        ),
        "cfm-calculator": (
            "CFM is cubic feet per minute. You need the room's volume and how many times per hour the air should be replaced.",
            "A 10 by 10 by 8 ft room is 800 cubic feet. At 6 air changes an hour, the fan needs 800 × 6 / 60 = 80 CFM.",
            "Double the air changes and the CFM should double. The minutes for one full change should halve.",
            "A hood or a spray booth may need a code minimum this estimate does not know.",
        ),
        "air-changes-calculator": (
            "Enter the room's cubic feet and the fan's CFM. Air changes per hour are CFM times 60, divided by the volume.",
            "An 80 CFM fan in an 800 cubic foot room gives 6 air changes an hour. One full change takes 10 minutes.",
            "If you type the room in inches, the volume is huge and the air changes collapse toward zero. Use feet.",
            "It does not measure the fan. It uses the CFM you claim the fan moves.",
        ),
        "lumber-calculator": (
            "Board feet are thickness in inches times width in inches times length in feet, divided by 12, times the number of boards.",
            "A 2×4 that is 8 feet long is 2 × 4 × 8 / 12 = 5.33 board feet. Ten of them are 53.3 board feet. The price is that volume times the price per board foot.",
            "A 2×4 is the nominal size. If you are buying surfaced lumber, the actual thickness is less, but board feet are still sold on the nominal size unless the yard says otherwise.",
            "It does not add waste for cuts. Add waste yourself before you order.",
        ),
        "deck-calculator": (
            "You need the deck length and width, the board width, the gap between boards, and the joist spacing.",
            "Boards run across the joists. A wider gap means fewer boards and a slightly different count. Joists are spaced along the other direction, often 16 inches on center, so the count is the span divided by the spacing, plus one for the end.",
            "Square footage should stay length times width even when the board count changes. If the area moves when you only change the gap, the fields are tied together incorrectly.",
            "This is a material count. It does not design the ledger, the footings, or the load.",
        ),
        "spray-foam-calculator": (
            "Board feet of foam are square feet of wall times the thickness in inches. Kits are sold by how many board feet they cover.",
            "A 200 square foot wall at 2 inches is 400 board feet. If a kit covers 600 board feet, one kit is enough for that wall and not enough for a second wall of the same size.",
            "Doubling the thickness should double the board feet and the cost. The wall area should not change.",
            "It does not choose open-cell versus closed-cell yield. Use the yield printed on the kit you will buy.",
        ),
        "miter-angle-calculator": (
            "For a frame with equal sides, the miter angle on each piece is half of the corner. A square has 90 degree corners, so each miter is 45 degrees.",
            "A regular hexagon has interior corners of 120 degrees, so each miter is 60 degrees from the square reference people expect, which is a 30 degree cut off square. Read the label: 'miter angle' and 'degrees off 90' are not the same number.",
            "A square should show 45 degrees. If it does not, you are reading the interior corner instead of the saw setting.",
            "The saw setting assumes equal sides and a flat frame. A non-equal frame needs a different calculation.",
        ),
        "kerf-calculator": (
            "Kerf is the width the saw blade turns into sawdust. Each cut consumes one kerf. The number of pieces from one board is the usable length divided by piece length plus kerf, with care about the last piece, which may not need a trailing kerf.",
            "A 96 inch board, 10 inch pieces, and a 1/8 inch kerf does not yield 9.6 pieces. After eight pieces you have used eight lengths and seven or eight kerfs, depending on whether the last cut is required. The page's piece count should be a whole number you can actually cut.",
            "Set the kerf to 0. The count should match the board length divided by the piece length, ignoring the blade. Put the kerf back and the count should stay the same or drop.",
            "A bowed board or a trimmed factory end eats length this page does not see.",
        ),
        "ohms-law-calculator": (
            "Ohm's law is V = I × R. Watts are V × I. Give the page any two of voltage, current, and resistance and it solves the others.",
            "A 12 volt supply across 6 ohms draws 2 amps and uses 24 watts. If you instead enter 12 volts and 2 amps, the resistance should come back as 6 ohms.",
            "Check that volts equal amps times ohms on the numbers the page shows. All four figures should describe the same circuit.",
            "This is DC ohm's law for a resistive load. Motors, capacitors, and power factors are a different page.",
        ),
        "voltage-drop-calculator": (
            "Voltage drop grows with current, with the length of the run, and with the resistance of the wire. Copper drops less than aluminum at the same gauge. A thicker gauge (a smaller AWG number) drops less.",
            "Percent drop is the drop divided by the supply voltage. A 3% target on 120 volts is 3.6 volts. A long run at a high amperage can miss that target on a thin wire.",
            "Double the distance and the drop should roughly double. Switch from copper to aluminum and the drop should rise.",
            "Ampacity, the heat limit of the wire, is a separate rule from voltage drop. A wire can pass the drop test and still be too thin for the current.",
        ),
        "wire-size-calculator": (
            "Enter amps, one-way or round-trip distance as the form defines it, voltage, and the percent drop you will accept. The page picks the smallest gauge that stays inside that drop.",
            "A longer run or a higher load steps you to a thicker wire. Read the AWG it names and the percent drop that gauge actually produces, not only the gauge.",
            "Tighten the allowed drop from 5% to 3%. The gauge should stay or get thicker, never thinner.",
            "Local electrical code and the breaker size can require a thicker wire than voltage drop alone. This page does not replace that.",
        ),
        "kw-to-kva-calculator": (
            "kW is real power. kVA is apparent power. kW = kVA × power factor. A power factor of 1 means they match. A motor with a power factor of 0.8 needs more kVA than its kW.",
            "10 kW at a power factor of 0.8 is 12.5 kVA. Single-phase amps are watts divided by voltage. Three-phase amps are watts divided by voltage times square root of 3 times power factor.",
            "Set the power factor to 1. kW and kVA should match. Lower it and kVA should rise.",
            "Nameplate ratings and starting current are not this conversion. Use the numbers on the equipment plate.",
        ),
        "electricity-cost-calculator": (
            "Cost is watts turned into kilowatts, times hours, times the price per kWh. A 1000 watt load for 1 hour is 1 kWh.",
            "A 100 watt bulb for 5 hours a day uses 0.5 kWh a day. At 0.20 per kWh that is 0.10 a day, about 3 a month at 30 days.",
            "The monthly figure should be about 30 times the daily figure. If you entered hours per month in the per-day box, the cost is 30 times too high.",
            "Standby draw and a utility's tiered rates are not included unless you fold them into the price you type.",
        ),
        "ev-charging-cost-calculator": (
            "Energy for the trip is miles divided by the efficiency in miles per kWh, or miles times kWh per mile, depending on the field. Hours on the charger are that energy divided by the charger kW. Cost is the energy times the price per kWh.",
            "A car that uses 0.30 kWh per mile needs 30 kWh for 100 miles. At 0.15 per kWh the energy costs 4.50. A 7 kW charger takes about 30 / 7 hours, a bit over 4 hours.",
            "A faster charger should cut the hours and leave the cost alone, if the price per kWh stays the same. Cost changes only when energy or price changes.",
            "Charging losses, cold weather, and a session fee are extra. The page uses the efficiency you type.",
        ),
        "closing-cost-calculator": (
            "Add the buyer costs the form lists: lender fees, title, inspection, appraisal, and prepaid taxes and insurance. The total is a sum, not a percent, unless a line is marked as a percent of the price.",
            "Prepaid tax is not a fee you lose. It is money set aside for a bill you would pay anyway. Read the total with and without prepaids before you call the whole sum a 'cost.'",
            "Each line you set to zero should lower the total by that line. That catches a double-counted field.",
            "A lender's loan estimate is the real list. This page adds the numbers you have gathered.",
        ),
        "down-payment-calculator": (
            "The loan amount is the price minus the down payment. Compare 3%, 5%, 10%, 20%, and your own percent.",
            "Below 20% down, lenders often charge PMI. The page flags that likelihood. It is not a quote for the PMI premium.",
            "20% of the price should produce a loan of 80% and clear the PMI flag. 10% should keep the flag.",
            "Assistance programs and a seller credit can change the cash you bring. They are not in the percent buttons.",
        ),
        "refinance-calculator": (
            "Enter the current balance, rate, and remaining term, and the new rate, term, and closing costs. Break-even months are the closing costs divided by the monthly savings.",
            "A lower payment from a longer term can still cost more interest over the life of the loan. Read the payment and the total interest. They answer different questions.",
            "If the new payment is higher, the monthly savings are zero or negative and there is no break-even from payment savings. You might still be paying the balance down faster.",
            "Points, cash-out, and the cost of resetting a 30-year clock are visible only in the fields you fill.",
        ),
        "rental-property-calculator": (
            "Cap rate is yearly net operating income divided by the price, before the mortgage. Cash flow is rent minus operating costs minus the mortgage payment. Cash-on-cash is the yearly cash flow divided by the cash you invested.",
            "A property can have a fine cap rate and negative cash flow if the mortgage payment is larger than the net rent. Look at both.",
            "Set the loan to zero. Cash flow should rise by about the mortgage payment, and cap rate should stay put, because cap rate ignores the loan.",
            "Vacancy, repairs, and taxes you forgot to type will erase a thin cash-flow number.",
        ),
        "seller-net-calculator": (
            "Net to the seller is the sale price minus commission, the mortgage payoff, closing costs, and repairs.",
            "A 400,000 sale with a 6% commission is 24,000 off before the loan payoff. A payoff of 250,000 and 8,000 of costs leaves 118,000, before any repair you still have to do.",
            "The commission should move when you change the percent, and it should be the percent times the price, not times the equity.",
            "Prorated taxes and a buyer credit can change the closing statement. Add them if you already know them.",
        ),
        "loan-comparison-calculator": (
            "Enter both loans: amount, rate, and term. Compare the monthly payment, the total interest, and the total paid.",
            "A lower rate wins on interest if the amount and the term match. A shorter term can have a higher payment and still cost less overall.",
            "If loan A and loan B have the same three inputs, the three results should match. That is the sanity check.",
            "Points and fees belong in an APR comparison if you are looking at upfront cost, not only the note rate.",
        ),
        "budget-calculator": (
            "Enter monthly income and the amounts you spend on housing, food, transport, debt, and the other lines. Left over is income minus those amounts. Savings rate is what you keep, divided by income.",
            "A common check is whether housing is eating the budget. The page does not enforce a 30% rule. It shows your number next to the income you typed.",
            "The leftover plus the spending lines should equal the income. If they do not, a line was left out or entered twice.",
            "An annual bill you forgot to divide into a monthly amount will make the leftover look safer than it is.",
        ),
        "vehicle-depreciation-calculator": (
            "Declining balance takes a percent off the current value each year, not off the original price.",
            "A 30,000 car losing 15% a year is worth 25,500 after one year and 25,500 × 0.85 after two years, which is 21,675. A flat 15% of 30,000 each year would be a different, lower path.",
            "Year 0 should be the price you typed. Year 1 should be that price times one minus the rate.",
            "A real resale price depends on miles, condition, and the market. The percent is your assumption.",
        ),
        "marketplace-fee-calculator": (
            "Net profit is the sale price minus the marketplace fee, shipping, and the product cost. Margin is that profit divided by the sale price.",
            "On a 40 sale with a 15% fee, the fee is 6. If shipping is 5 and the item cost is 18, profit is 40 − 6 − 5 − 18 = 11, and the margin is 11/40 = 27.5%.",
            "The fee should be the percent times the price the form says the percent applies to. Some marketplaces charge the percent on price plus shipping. Read that label.",
            "Returns, ads, and a payment hold are not in the profit until you type them as costs.",
        ),
        "tithing-calculator": (
            "A tithe is the percent you choose, traditionally discussed as 10%, of the income period you mean: weekly, monthly, or yearly.",
            "10% of a 4,000 monthly income is 400 a month, which is 4,800 a year. 10% of the yearly income should match twelve monthly tithes if the income is flat.",
            "Change the percent from 10 to 5 and the amount should halve. The income period should not change.",
            "The page multiplies. It does not decide whether the base is gross or net. You choose the income figure you type.",
        ),
        "retirement-calculator": (
            "The projection compounds the current balance and adds each monthly contribution at the annual return you type, for the years you type.",
            "Contributions matter more when the balance is small. The return matters more when the balance is large. Run it once with contributions and once without to see which one is doing the work.",
            "At a 0% return, the ending balance should equal the start plus every contribution, with no growth.",
            "It does not model a crash, a pension, Social Security, or the tax on withdrawals.",
        ),
        "employee-cost-calculator": (
            "Loaded cost is salary plus benefits plus employer payroll tax. Benefits are often entered as a percent of salary. The employer tax is a separate percent.",
            "A 60,000 salary with 20% benefits and 8% employer tax costs 60,000 × 1.28 = 76,800 a year, if both percents apply to salary. Read whether the tax applies to salary only or to salary plus benefits.",
            "The loaded cost should be higher than the salary. If it is not, a percent field is empty or was entered as a whole number in the wrong way.",
            "Overtime, equipment, and recruiting are extra. They are not in the two percents unless you raise them to include those costs.",
        ),
        "absorption-rate-calculator": (
            "Months of supply is the number of homes for sale divided by the number sold per month. Absorption rate is the share of the inventory that sold.",
            "If 120 homes are listed and 30 sell in a month, that is 4 months of supply, and the monthly absorption is 30/120 = 25%.",
            "Double the sales and the months of supply should halve. The page is only as good as the sold count you typed.",
            "One neighbourhood's sales do not describe a whole city. Use the same geography for listings and sales.",
        ),
        "car-trade-equity-calculator": (
            "Equity is the trade-in offer minus the loan payoff. Positive equity means the offer covers the loan. Negative equity means you still owe more than the offer.",
            "A 15,000 offer and a 12,000 payoff is 3,000 of positive equity. A 15,000 offer and an 18,000 payoff is 3,000 you still owe, which a dealer may roll into the next loan.",
            "Sales tax with a trade-in is often charged on the difference, not the full price of the next car, in states that work that way. Compare the two tax lines. The trade-in case should be lower when the offer is real.",
            "Tax rules differ by state. The page shows the comparison from the prices you enter. It does not know your state's exceptions.",
        ),
        "business-valuation-calculator": (
            "A small-business estimate here is a multiple times seller's discretionary earnings, or a multiple times revenue. You choose the multiples.",
            "Earnings of 100,000 at a 2.5 multiple is 250,000. Revenue of 500,000 at a 0.6 multiple is 300,000. Those are two opinions, not one fact. The business is not worth both.",
            "Doubling the multiple should double that estimate. If you are comparing earnings and revenue methods, label which multiple belongs to which base.",
            "A buyer prices risk, customers, and the owner's role. A multiple from a different industry will mislead you.",
        ),
        "aquarium-calculator": (
            "Volume of a rectangular tank is length times width times height. US gallons are cubic inches divided by 231. Litres are cubic centimetres divided by 1,000.",
            "A 48 × 12 × 16 inch tank is 9,216 cubic inches, about 39.9 US gallons. A heater is often sized around a few watts per gallon, and a water change is the percent of that volume you choose.",
            "The litre figure times about 0.264 should be near the US gallon figure. Salt dose should scale with the litres or gallons you are treating, not with the empty glass.",
            "Gravel and rocks displace water, so the filled volume is less than the glass volume. Subtract that if you are dosing medicine.",
        ),
        "coffee-ratio-calculator": (
            "The ratio is water weight divided by coffee weight. A 1:16 pour-over means 16 grams of water per gram of coffee.",
            "20 grams of coffee at 1:16 needs 320 grams of water. Espresso is closer to 1:2. Cold brew is a different, often stronger, ratio. Use the preset that names the brew you are making.",
            "Doubling the coffee dose should double the water if the ratio stays the same.",
            "A ratio is a starting point. Grind and time still decide the cup. The page does not brew it.",
        ),
        "3d-print-cost-calculator": (
            "Filament cost is grams used divided by grams on the spool, times the spool price. Electricity is hours times the printer's watts turned into kilowatts, times your price per kWh.",
            "A 1 kg spool that cost 20, with a 50 gram print, is 1 of plastic. A 100 watt printer for 4 hours uses 0.4 kWh. At 0.15 per kWh that is 0.06 of electricity. The plastic dominates.",
            "The total should be plastic plus electricity, plus any wear or labour field the form has. Hide electricity and the total should fall by that small amount.",
            "Failed prints and supports are grams you have to include yourself. The slicer estimate of grams is the input, not a promise.",
        ),
        "cat-age-calculator": (
            "A cat's first year is not one human year. Common charts treat the first year as about 15 human years and the second as about 9 more, then about 4 human years per cat year after that.",
            "A 2-year-old cat is often counted near 24 in human terms. A 10-year-old cat is often counted near 56. The page should follow the curve it names, not a flat multiply-by-seven.",
            "A 1-year-old and a 2-year-old should not be 7 and 14. If they are, the page is using the dog myth.",
            "This is a conversation chart, not a vet's age. Health depends on teeth, weight, and bloodwork.",
        ),
        "plant-spacing-calculator": (
            "Square spacing puts each plant on a grid. The count is the bed length divided by the spacing, times the bed width divided by the spacing. Triangular spacing staggers the rows and fits more plants.",
            "A 4 ft by 8 ft bed with plants 12 inches apart is 4 plants by 8 plants, which is 32, if you start at the edge the way the form assumes. A half-spacing inset from the edge lowers the count.",
            "Triangular spacing should show more plants than square spacing for the same bed and the same spacing, or explain the inset it used.",
            "Paths, a trellis, and the mature width of the plant are your judgment. The page only tiles the rectangle.",
        ),
        "compost-calculator": (
            "A common target is about 30 parts carbon (browns) to 1 part nitrogen (greens) by weight, though gardeners often mix by volume. The page tells you which side you are heavy on.",
            "If the mix is too heavy on browns, add greens. If it is too heavy on greens, add browns. The amount to add is the gap between your ratio and the target.",
            "Adding the amount the page suggests should move the ratio onto the target when you calculate it again.",
            "Wet scraps and dry leaves do not have the same density. Volume ratios are a guide. Smell and heat tell you how the pile is actually doing.",
        ),
        "hull-speed-calculator": (
            "Displacement hull speed in knots is about 1.34 times the square root of the waterline length in feet.",
            "A boat with a 25 ft waterline has a hull speed near 1.34 × 5 = 6.7 knots. In mph that is 6.7 × 1.151, about 7.7 mph.",
            "A longer waterline should raise the speed with the square root, not in a straight line. Quadrupling the length doubles the hull speed.",
            "Planing hulls and catamarans are not limited by this formula. It describes a displacement hull.",
        ),
        "fuel-mix-calculator": (
            "A 50:1 mix is 50 parts gasoline to 1 part oil. Oil in ounces is the gallons of gas times 128, divided by the ratio.",
            "One US gallon at 50:1 needs 128/50 = 2.56 ounces of oil, about 76 ml. At 40:1 the same gallon needs more oil, 3.2 ounces.",
            "A smaller ratio number means richer oil. 25:1 should call for about twice the oil of 50:1.",
            "Use the ratio printed on the engine. A chainsaw and a boat motor do not share a guess.",
        ),
        "molarity-calculator": (
            "Molarity is moles per litre. Moles are grams divided by the molar mass in grams per mole.",
            "58.44 grams of NaCl is one mole. Dissolved in 1 litre, that is a 1 molar solution. To make 0.5 litres of 0.5 M, you need 0.25 moles, about 14.6 grams.",
            "The grams the page asks you to weigh should scale with both the volume and the molarity. Double either one and the grams should double.",
            "The molar mass has to be the substance you are weighing. A hydrate and an anhydrous salt are different masses.",
        ),
        "hexagon-quilt-calculator": (
            "A regular hexagon's area depends on the side length. Fabric area adds the seam allowance around each piece, then multiplies by how many hexes you need.",
            "Seam allowance increases each side you cut, so the cut size is larger than the finished size. Forgetting it makes every piece short.",
            "Doubling the number of hexes should double the fabric area. Changing the seam allowance should change the cut size and not the finished size.",
            "A particular quilt pattern's waste from the way hexes nest on the cloth is extra. The page estimates the piece area.",
        ),
    }
    if slug in facts:
        return facts[slug]
    return generic_note(name, desc)


def health_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    facts = {
        "water-intake-calculator": (
            "The estimate scales with body weight, then adds something for exercise and climate. Read the result in litres, cups, and bottles so you can match the bottle you own.",
            "A common starting point is about 30–35 ml per kilogram of body weight, before a hot day or a long workout adds more. The page's add-ons should raise the total, not replace it.",
            "A heavier body should get a higher base. Exercise minutes should add, not multiply the whole day by a huge factor, unless the form says that is what it does.",
            "Thirst, sweat, and a doctor's fluid limit beat a general estimate. This is not medical advice for kidney disease or heart failure.",
        ),
        "macro-calculator": (
            "Protein, carbohydrate, and fat grams have to add up to the calorie target. Protein and carbohydrate are about 4 kcal per gram. Fat is about 9.",
            "A 2,000 kcal day with 150 g protein and 70 g fat leaves 2,000 − 600 − 630 = 770 kcal for carbohydrate, about 192 g. A 'low carb' preset moves those grams. It does not change the calorie target unless you change calories.",
            "Check that grams times their calories land near the daily target. A rounding gap of a few calories is normal. A gap of hundreds means a preset overwrote a field.",
            "It splits calories. It does not prescribe a medical diet.",
        ),
        "heart-rate-zone-calculator": (
            "Karvonen uses heart-rate reserve: maximum heart rate minus resting heart rate. A zone is a percent of that reserve, added back onto the resting rate.",
            "If max is 180 and resting is 60, the reserve is 120. Zone work at 60% is 60 + 0.60 × 120 = 132 beats per minute. A plain percent of max, without the resting rate, would have said 108. Those are different methods.",
            "A higher resting rate should raise the zone beats if max stays put, because you start from a higher floor.",
            "The 220-minus-age maximum is a rough population guess. A measured max is better. This is not a clearance to train hard.",
        ),
        "calories-burned-calculator": (
            "MET values estimate how hard an activity is. Calories are about MET times body weight in kilograms times hours.",
            "Walking at a moderate MET, a heavier person burns more than a lighter person for the same hour. Doubling the minutes should double the calories.",
            "Compare two activities at the same weight and duration. The one with the higher MET should burn more.",
            "A fitness tracker that sees your heart rate is a different measurement. MET tables are averages.",
        ),
        "one-rep-max-calculator": (
            "A 1RM estimate predicts the heaviest single lift from a lighter set. The Epley idea is weight times (1 + reps / 30). Other formulas differ a little.",
            "100 kg for 5 reps is about 100 × (1 + 5/30) = 117 kg under Epley. The training table then shows percents of that 117, such as 85% for heavier sets.",
            "One rep at a weight should return that same weight as the max. If it does not, the formula is being applied to a rep you did not intend.",
            "Estimates get worse above about 10 reps. This does not know your form or an injury.",
        ),
        "pace-calculator": (
            "Pace is time divided by distance. A predicted race time assumes you hold a related pace, which a real race may not allow.",
            "10 kilometres in 50 minutes is 5:00 per kilometre and about 8:03 per mile. A 5K prediction from that pace is half the distance only if you can hold the same speed, which most people cannot.",
            "Double the distance at the same pace and the time should double. Switch miles to kilometres and both the pace and the distance label should change together.",
            "Hills, heat, and a crowd are not in the straight-line pace.",
        ),
        "bac-calculator": (
            "The Widmark estimate uses alcohol consumed, body weight, and a sex-based factor for body water, then subtracts alcohol burned over time.",
            "More drinks and less body weight raise the estimate. Time since the first drink lowers it, often by about 0.015 BAC per hour in the simple model, which is an average, not your liver.",
            "At zero drinks the result should be zero. One drink just consumed should not already be zero.",
            "This is not a legal measurement. A breath or blood test is. Do not use the number to decide whether to drive.",
        ),
        "protein-intake-calculator": (
            "The target is a range of grams per kilogram of body weight. The range depends on the goal you pick: general health, building muscle, or losing fat while keeping muscle.",
            "A common gym range for building muscle is about 1.6–2.2 g per kilogram. At 70 kg that is about 112–154 g a day. The page should show a range, not a single magic gram.",
            "A higher body weight should raise the grams. Switching the goal should move the range. The body weight should not change when you only switch the goal.",
            "Kidney disease and other conditions can require a lower protein target. This calculator does not know that.",
        ),
        "waist-to-hip-ratio-calculator": (
            "The ratio is waist circumference divided by hip circumference. Measure the waist at the narrowest point or at the navel, the same way each time, and the hips at the widest point.",
            "A waist of 80 cm and hips of 100 cm is 0.80. Risk categories differ for men and women. A ratio that is higher means more of the circumference is at the waist.",
            "If you swap waist and hip, the ratio jumps above 1 for most people. That is a clue the fields are reversed.",
            "The category is a screening chart, not a diagnosis.",
        ),
        "body-surface-area-calculator": (
            "Mosteller's formula is the square root of (height in cm times weight in kg, divided by 3600). Du Bois is an older formula with a different curve. They should be close, not identical.",
            "For 170 cm and 70 kg, Mosteller's area is the square root of (170 × 70 / 3600), which is the square root of about 3.31, about 1.82 square metres.",
            "Both formulas should rise if weight rises. If one of them does not, that formula's inputs were left in the wrong unit.",
            "Drug dosing from body surface area is a clinician's decision. Do not dose from this page.",
        ),
    }
    if slug in facts:
        return facts[slug]
    return generic_note(name, desc)


def image_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    pair = {
        "webp-to-png": "WebP can be a photo or a lossless image. PNG keeps transparency and does not use JPG's blocky compression. The PNG is often larger.",
        "webp-to-jpg": "JPG has no transparency. Any clear pixels in the WebP become a solid background. The file gets smaller because JPG throws away detail.",
        "png-to-jpg": "PNG transparency is lost. Soft edges and screenshots of text look worse after JPG compression. Set the quality high if the image contains text.",
        "jpg-to-png": "PNG does not repair a JPG. It wraps the same pixels in a lossless file, which is usually larger. Use it when a tool downstream refuses JPG.",
        "png-to-webp": "WebP can keep transparency and usually weighs less than PNG. Check a logo on a non-white background so you notice if the alpha channel disappeared.",
        "jpg-to-webp": "WebP at a similar visual quality is usually smaller than JPG. Zoom to 100% on a face or a fine pattern before you delete the original.",
        "heic-to-jpg": "HEIC is the iPhone photo format. The JPG is the shareable copy. Orientation can be stored sideways in the file. The preview should look upright.",
        "svg-to-png": "SVG is vectors. PNG is pixels. Pick the pixel size you will display, because a small PNG looks soft if you stretch it later.",
        "png-to-svg": "Tracing a photo into vectors guesses shapes. Logos with flat colours trace cleanly. A portrait will not become a crisp illustration.",
        "image-to-base64": "The result is a data URI you can paste into HTML or CSS. It is longer than the file. It does not upload the image anywhere.",
        "base64-to-image": "Paste the data URI or the bare Base64. A missing comma after the media type, or a wrapped line, is the usual reason the preview is blank.",
        "jfif-to-jpg": "JFIF is a JPEG variant with a different file name. The pixels are already JPEG. This gives you a .jpg file other software will open.",
        "jfif-to-png": "The pixels stay photographic. PNG will not add detail that JFIF already discarded. Expect a larger file.",
        "bmp-to-jpg": "BMP is uncompressed pixels. JPG will shrink it a lot and soften fine detail. Keep the BMP if you still need to edit.",
        "bmp-to-pdf": "Each BMP becomes a page or an image on a page. The PDF is a wrapper for sharing, not a smaller master of the bitmap.",
        "avif-to-jpg": "AVIF is a newer photo format some older apps cannot open. JPG is the compatible copy. Transparency, if the AVIF had it, becomes a background.",
        "avif-to-webp": "Both are modern photo formats. WebP is the one to pick when the destination accepts WebP but not AVIF. Compare file size at the same visual size.",
        "gif-to-video": "The animation becomes a WebM video. Video does not use GIF's 256-colour limit in the same way, so the motion can look cleaner, but a very old device may not play WebM.",
        "gif-to-png": "Every frame is exported as its own PNG, zipped. The timing of the animation is not inside a single PNG. You get the frames, not the player.",
        "gif-to-jpg": "Frames become JPGs. Transparency in a frame becomes a solid colour, and the animation is no longer one file.",
        "gif-to-webp": "Animated WebP can keep the motion in one file and often weighs less than the GIF. Play it once to confirm the frame timing survived.",
    }
    actions = {
        "resize-image": "Changing the pixel size does not add detail. Enlarging a small photo makes it blurry. Shrinking is safer. Keep the aspect lock on unless you mean to stretch.",
        "compress-image": "Quality is a deliberate loss. Text and logos fall apart before photographs do. Compare at 100% zoom, not as a thumbnail.",
        "crop-image": "The crop throws away pixels outside the rectangle. A fixed aspect ratio such as 1:1 will cut whichever side does not fit. Nothing outside the crop can be restored from the download.",
        "rotate-image": "A 90 degree turn swaps width and height. An arbitrary angle leaves triangular corners that are empty. Those corners are part of the new canvas.",
        "flip-image": "Horizontal flip is a mirror. Text in the image will read backwards. Vertical flip turns it upside down. The file's pixels change. The original is untouched.",
        "favicon-generator": "A favicon is the tiny icon in a browser tab. It needs to be simple at 16 and 32 pixels. The page builds those sizes and an ICO from the image you upload.",
        "image-to-ico": "ICO can hold several sizes in one file. Windows uses the size that fits the place it draws. Start from a square PNG so the icon is not stretched.",
        "meme-generator": "Top and bottom captions sit in the margin of the picture. Long text wraps or overflows. Download and read the caption at the size you will post.",
        "add-watermark-to-image": "A watermark is burned into the pixels of the download. Place it where it does not cover the subject, and keep an unmarked original.",
        "image-color-picker": "The HEX and RGB values are the pixel you clicked, not a nearby average, unless the tool says it samples an area. Screen colour profiles can make the same pixel look different on another monitor.",
        "color-extractor-from-image": "A palette is a summary of common colours, not every colour in the photo. A small logo colour can be missed if most of the photo is one wall.",
        "collage-maker": "The grid sets the aspect of each cell. Photos are cropped to the cell. Check faces near the edges before you download.",
        "combine-images": "Stitching keeps each photo whole and places them in a row or a column. Different heights leave empty bands unless the page scales them to match.",
        "passport-photo-maker": "Passport and visa sizes are exact millimetre targets. The head has to sit inside the frame the spec describes. A crop that only looks square can still fail the official size.",
        "grayscale-image": "Grayscale keeps the brightness and drops the hue. A red and a green of the same brightness become the same gray. The download is not a colour file with a filter you can undo.",
        "blur-image": "Blur mixes neighbouring pixels. A small radius softens. A large radius hides detail. If you blur only a region, the edge of that region should be where you set it.",
        "pixelate-image": "Pixelate replaces a region with big blocks so a face, a plate, or a message cannot be read. The rest of the photo stays sharp. You cannot un-pixelate the download.",
        "image-to-pdf": "The PDF wraps the image on a page. It does not OCR the words in the picture. The page size follows the image unless you pick a paper size.",
        "circle-crop-image": "The download is a circle with transparent corners if the format allows transparency. JPG cannot store those corners. Use PNG if the circle must sit on another background.",
        "gif-maker": "The animation's frame order is the order of the images you added. Delay is the time each frame stays. A short delay looks smooth and makes a larger, busier file.",
        "gif-resizer": "Resizing a GIF resizes every frame. A smaller width and height lowers the file size and softens the picture. Presets such as a story size crop or fit. Read which one you selected.",
        "gif-rotator": "Rotation applies to every frame, so the motion still lines up. A 90 degree turn swaps the width and height of the animation.",
        "gif-trimmer": "Trimming keeps a start frame and an end frame and drops the rest. The timing of the frames you keep should stay as it was.",
        "gif-optimizer": "Optimization drops extra colours or frames to shrink the file. Look at gradients and text. Those break first.",
        "aspect-ratio-calculator": "An aspect ratio is width divided by height, reduced. 1920 by 1080 is 16:9. Scaling to a new width keeps the height in that same ratio unless you unlock it.",
        "duplicate-photo-finder": "Exact duplicates share a file hash. Similar photos are grouped with a perceptual hash, so a resize can still match. The suggestion to keep the highest resolution is a suggestion. You delete nothing until you say so. The scan stays in the browser.",
        "home-color-visualizer": "You paint regions of a photo, not the room itself. Lighting in the photo changes the colour you see. Compare two colours on the same wall before you buy paint.",
        "screenshot-auto-anonymizer": "The blur or blackout is burned into the download. Faces, text, cards, and the other detectors can miss something. Look at the result before you send it. The original file stays on your device.",
    }
    if slug in pair:
        bring = f"Start from the original {slug.split('-to-')[0].upper()} file, not a screenshot of it."
        example = pair[slug]
        check = "Open the download at the size you will use. Check transparency, text, and the file size against the original."
        stop = f"{name} converts the file. It does not recover detail the source never had."
        return bring, example, check, stop
    if slug in actions:
        return (
            f"Use the original image. {desc.rstrip('.')}.",
            actions[slug],
            "Compare the download with the original at 100% zoom on the part you care about: a face, a line of text, or the edge of the crop.",
            f"{name} changes the copy you download. It does not edit the file still sitting in your folder until you replace it.",
        )
    return generic_note(name, desc)


def pdf_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    facts = {
        "merge-pdf": "Page order in the download is the order you set, file by file. A blank page you did not notice in one file stays in the merge. Open the last page of each original and confirm it landed where you think.",
        "split-pdf": "A range such as 2–4 keeps those pages and drops the rest into other files. Pages are numbered from 1 as the PDF counts them, which may not match a number printed on the page.",
        "compress-pdf": "Compression shrinks images inside the PDF and can leave text alone. A scanned page is a picture, so it gets softer. If the text was real text, it should still be selectable.",
        "rotate-pdf": "Rotation is saved into the file. A viewer that ignored a display-only rotate will now show the page turned. Check every page you marked, not only the first.",
        "delete-pdf-pages": "Deleted pages are gone from the download. The page count should fall by the number you removed. The original file is unchanged.",
        "extract-pdf-pages": "Extract copies the pages you name into a new, shorter PDF. The original still has them. This is the tool when you want a chapter without destroying the full file.",
        "organize-pdf": "Drag order is the new page order. A thumbnail that looks similar is still a different page. Check the first and last page after you save.",
        "jpg-to-pdf": "Each JPG becomes visual content on a PDF page. The words in the photo are not selectable text. Order the images before you build the file.",
        "png-to-pdf": "PNG transparency becomes a background on the PDF page, often white. A logo that looked clear on a checkerboard will sit on that background.",
        "pdf-to-jpg": "Each page is rendered to a picture. Selectable text becomes pixels. Zoom and choose a resolution that keeps the text readable, because you cannot select it later.",
        "pdf-to-png": "PNG rendering keeps sharper edges than JPG and a larger file. Use it for a figure or a stamp. A full scanned contract will be heavy.",
        "images-to-pdf": "The PDF page order is the image order you set. Mixed orientations need a look at each page, because a portrait phone photo on a landscape page leaves large margins.",
        "extract-images-from-pdf": "This pulls images that are embedded as images. A scanned page may be one big image. A chart drawn as vectors may not come out as a picture at all.",
        "add-page-numbers-to-pdf": "The number is drawn onto the page. It can collide with a number already printed in the document. Pick a corner that is empty.",
        "add-watermark-to-pdf": "A watermark is stamped on the pages you choose. Text that was selectable usually stays selectable. The stamp itself is part of the new file.",
        "crop-pdf": "Cropping hides the margin in the page box. It does not always delete the hidden content from the file. Do not use crop to remove a secret. Delete or redact for that.",
        "protect-pdf": "The password is the only way back in. The page encrypts the download. It does not store the password for you. Test the locked file before you delete the original.",
        "unlock-pdf": "You must already know the password. The page removes it from a copy so a workflow that rejects locked files can open it. It does not crack a password.",
        "sign-pdf": "The signature is placed where you drag it, on the pages you pick. Draw, type, or upload the mark, then open the download and confirm the placement did not cover a line you still need to read.",
        "edit-pdf": "Added text and shapes sit on top of the page. Existing paragraph text does not reflow like a word processor unless the tool says it does. Check alignment on the downloaded file.",
        "fill-pdf-form": "Fillable fields accept what you type. Flattening then turns those fields into static ink so the values cannot be edited as fields. Fill first, then flatten when you are done.",
        "flatten-pdf": "Annotations and form values become ordinary page content. You can no longer tab into the fields. Do this when you want a file that looks the same on every computer.",
        "resize-pdf": "Scaling to A4 or Letter changes the page box. Content may shrink to fit or be clipped. Look at a page with a footer. Footers are the first thing cut off.",
        "reverse-pdf-pages": "The last page becomes the first. A document that was pages 1 to 10 reads 10 to 1. This is useful for a stack that was scanned backwards.",
        "split-pdf-in-half": "Each page is cut on a vertical or horizontal line into two pages. A two-up scan of a book becomes one page per side. The cut is in the middle unless you move it.",
        "extract-text-from-pdf": "Only text that is really text comes out. A scan is a picture and yields little or nothing. If the result is empty, the PDF needs OCR, which this page is not doing.",
        "pdf-page-counter": "The count is the number of pages in the file, not the number printed on the last page. A cover counts. A blank page counts.",
        "duplicate-pdf-pages": "The pages you pick are repeated in the file. The page count rises. Confirm you duplicated the page you meant, not the one next to it.",
        "pdf-to-word": "The Word file is an editable reconstruction. Columns, headers, and tight layouts can shift. Read a page with a table before you send the DOC.",
        "word-to-pdf": "The PDF is the fixed look of the document. Fonts that are not embedded can substitute. Open the PDF and check a heading and a page number.",
        "txt-to-pdf": "Plain text has no layout. The PDF wraps the lines onto a page with the font and margins the tool uses. Long lines wrap. They do not stay one line unless they fit.",
        "csv-to-pdf": "Rows and columns become a table on the page. A wide sheet will wrap or shrink. Check a row in the middle, not only the header.",
        "excel-to-pdf": "This path expects a CSV export, not a live .xlsx workbook with several sheets. Export the sheet you mean, then convert that file.",
        "pdf-to-excel": "Tables are guessed from the positions of the text. A table with merged cells or a wrapped header will need cleanup in the spreadsheet. This is not a scan OCR.",
        "epub-to-pdf": "An ebook becomes paginated paper. Reflowable text gets a fixed page size. Images and chapter breaks can land in different places than the reader app.",
        "cbz-to-pdf": "A CBZ archive is images in a zip. The PDF puts those images in order as pages. The order of files inside the archive is the reading order.",
        "pdf-to-cbz": "Each PDF page becomes an image inside a comic archive. Text is no longer selectable. The reading order is the page order.",
        "pdf-to-pdf-a": "PDF/A is an archival shape: fonts embedded, features that break long-term viewing removed. The visual page should look the same. A form or a video inside the PDF may not survive.",
        "bank-statement-to-excel": "The CSV is only as good as the text in the statement. A scanned statement has no text to extract. Check a known transaction, the date, and the amount sign.",
    }
    if slug not in facts:
        return generic_note(name, desc)
    return (
        f"Use the PDF you mean to change, and read the page numbers the viewer shows. {desc.rstrip('.')}.",
        facts[slug],
        "Open the download and check page count, order, and one page you care about. If text used to be selectable, try to select it again.",
        f"{name} writes a new file. The original stays where it was until you delete it. A scan remains a picture unless this page says it reads text.",
    )


def unit_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    known = {
        "inches-to-cm-converter": "One inch is exactly 2.54 centimetres. Twelve inches is 30.48 cm. Type 1 and confirm 2.54 before you convert a measurement from a drawing.",
        "kg-to-lbs-converter": "One kilogram is about 2.20462 pounds. Ten kilograms is about 22.05 lb. The page should not treat a kilogram as 2 pounds.",
        "liters-to-gallons-converter": "A US gallon is about 3.785 litres. A UK gallon is about 4.546 litres. Read which gallon the form selected. They are not interchangeable.",
        "temperature-converter": "Water freezes at 0 °C, 32 °F, and 273.15 K. It boils at 100 °C and 212 °F. A gap of 10 °C is 18 °F, not 10 °F.",
        "length-converter": "Keep the pair straight: 1 metre is 3.28084 feet, 1 kilometre is 0.621371 miles, 1 inch is 2.54 cm. Convert a round number you know before a long one.",
        "weight-converter": "1 kilogram is 1000 grams and about 2.20462 pounds. 1 pound is 16 ounces. Ounces here are weight, not fluid ounces.",
        "time-zone-converter": "The conversion uses the offset of each zone on the date you pick, including daylight saving when that date observes it. A meeting at 09:00 in one zone is not 09:00 in the other.",
        "roman-numeral-converter": "1994 is MCMXCIV: 1000 + 900 + 90 + 4. A smaller numeral before a larger one subtracts. IIII is not the standard form. IV is.",
        "number-to-words-converter": "1042 in words is one thousand forty-two, without the word 'and' in the American style many cheques use, or with 'and' in other styles. Read which style the page printed before you put it on a cheque.",
        "binary-to-decimal-converter": "Binary 1010 is decimal 10, and hex A. 255 decimal is FF in hex and 11111111 in binary. A leading zero does not change the value.",
        "data-storage-converter": "In the decimal SI scale, 1 kilobyte is 1000 bytes and 1 megabyte is 1000 kilobytes. Some software uses 1024. The page should say which scale it used. A drive sold as 1 TB holds about 10^12 bytes, which an OS may show as less.",
        "fuel-consumption-converter": "MPG and L/100 km run in opposite directions. Lower L/100 km is better economy. You cannot add them. US gallons and UK gallons make two different MPG numbers.",
        "shoe-size-converter": "US, UK, and EU sizes are charts, not a physical law. A men's US size and a women's US size with the same number are not the same length. Use the chart that matches the shoe.",
        "cooking-measurement-converter": "A US cup is about 237 ml. A tablespoon is 3 teaspoons, about 15 ml. Grams depend on the ingredient. Flour and water do not weigh the same per cup. Convert volume to volume unless the form names the ingredient.",
    }
    detail = known.get(slug)
    if not detail:
        detail = f"{desc.rstrip('.')}. Convert a value you already know in both units, such as a round 1 or 10, and see that the other side matches the definition you trust. Then convert the measurement you actually have."
    return (
        f"Pick the two units before you type the quantity. {desc.rstrip('.')}.",
        detail,
        "Convert the result back the other way. You should land close to the number you started with. A large gap means the units are not the pair you think.",
        f"{name} converts units. It does not know which unit your drawing, recipe, or ticket required.",
    )


def color_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "color-picker": "The HEX you copy is the colour on the picker, six digits for opaque RGB. #FFFFFF is white and #000000 is black.",
        "hex-to-rgb": "#FF8000 is rgb(255, 128, 0). Two hex digits per channel, from 00 to FF.",
        "rgb-to-hex": "rgb(255, 128, 0) is #FF8000. Values belong between 0 and 255.",
        "hex-to-hsl": "HSL separates hue, saturation, and lightness. A gray has saturation 0. Lightness 0 is black and 100% is white, regardless of hue.",
        "hsl-to-hex": "Hue is a degree on the wheel, 0 and 360 both red. Saturation and lightness are percents. The HEX is the same colour in a form CSS accepts.",
        "rgb-to-hsl": "Changing lightness in HSL is easier than guessing RGB. Convert, move lightness, and convert back if you need the RGB again.",
        "rgb-to-cmyk": "CMYK is for print. The black plate (K) is not the same as a dark RGB. A pure RGB blue will not be a pure print blue.",
        "cmyk-to-rgb": "The RGB preview is an approximation of ink. Paper and the press shift it. Do not expect the screen to match the printed sheet exactly.",
        "hex-to-cmyk": "Start from the HEX you use on screen. The CMYK values are the print estimate. Hand the printer those numbers only if they asked for a conversion rather than a press profile.",
        "color-contrast-checker": "WCAG contrast is a ratio between the text colour and the background. 4.5:1 is the usual bar for normal text at AA. Large text can pass at 3:1. The ratio is about those two colours only.",
        "color-palette-generator": "A harmonious palette is a set of hues related by a rule, not five random colours. Lock the brand colour if the tool lets you, and read the HEX of each swatch.",
        "gradient-generator": "A CSS linear gradient needs an angle and at least two colour stops. The code you copy should contain both colours. A radial gradient starts from a centre instead of an edge.",
        "color-shades-generator": "A shade mixes the colour toward black. The HEX should get darker, not more saturated, as the step increases.",
        "color-tints-generator": "A tint mixes the colour toward white. Later steps should be lighter. The first step should still resemble the colour you typed.",
        "complementary-color-finder": "The complement sits opposite on the hue wheel, about 180 degrees away. Blue's complement is in the yellow-orange range. The HEX should not be a lighter version of the same hue.",
        "analogous-color-generator": "Analogous hues sit beside the base hue, often 30 degrees away. They look related. If one swatch is the opposite hue, the rule is wrong.",
        "triadic-color-generator": "A triad is three hues about 120 degrees apart. You should be able to see three distinct hues, not three shades of one.",
        "monochromatic-color-generator": "Every swatch keeps the same hue. Only lightness and saturation change. If the hue number jumps, it is not a mono palette.",
        "color-mixer": "The mix is a blend of the two colours you gave, at the percent you set. At 0% you should see the first colour. At 100% you should see the second.",
        "color-blindness-simulator": "The simulation shows how a given deficiency shifts the colours. It does not diagnose vision. Compare the original and the simulation on the pair you care about, such as red versus green status dots.",
        "box-shadow-generator": "The CSS is offset-x, offset-y, blur, spread, and colour. A larger blur is softer. Copy the declaration into a class and confirm the preview matches.",
        "text-shadow-generator": "Text shadow sits behind the glyphs. A tight offset and a small blur reads as depth. A huge blur washes the text out.",
        "color-contrast-checker": "Check the exact pair you will ship, not a nearby shade.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. Copy the value into the place you will use it, because a picker on this page and a monitor elsewhere can disagree.")
    return (
        f"Have the colour as a HEX, an RGB, or the two colours the form names. {desc.rstrip('.')}.",
        detail,
        "Paste the result back into the reverse converter when one exists. You should land near the colour you started with.",
        f"{name} does the colour math on the values you type. It does not see the rest of your page.",
    )


def text_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "word-counter": "A word is split on whitespace. 'New York' is two words. A hyphenated word is usually one. Reading time assumes a words-per-minute rate the page should name.",
        "character-counter": "Count with spaces and without spaces are different numbers. A social limit usually includes spaces. A trailing newline counts if it is in the box.",
        "case-converter": "Title case and sentence case follow different rules. Title case capitalizes most words. Sentence case capitalizes the first word and the word after a full stop. Names will be wrong if the tool does not know they are names.",
        "find-and-replace-text": "A plain replace changes every match. A regex replace treats dots and stars as patterns. Escape them if you mean a literal dot. Replace once on a copy and read a line you did not expect to change.",
        "remove-duplicate-lines": "Order of the first occurrence is kept. Later copies go. Blank lines may count as duplicates of each other. Decide that before you clean a list of emails.",
        "text-diff-checker": "Added and removed marks are against the two boxes, line by line or word by word as the tool says. A line that only lost a space can show as changed. That is a real change to a parser.",
        "morse-code-translator": "Letters are dots and dashes. Words are separated by a longer gap. A slash or a space in the output is the word gap. Play the audio if you have it and follow one word you know.",
        "binary-translator": "Each letter becomes eight bits in the encoding the page names. 'A' is 01000001 in ASCII. A space is a character too. Decode the bits and you should get the same sentence back.",
        "slug-generator": "A slug is lowercase, with spaces turned into hyphens and punctuation dropped. 'Hello, World!' becomes hello-world. The page does not check whether that URL is free.",
        "text-to-slug": "The same rules as a URL slug: lowercase, hyphens, no apostrophes. 'Don't Stop' should not keep the apostrophe.",
        "language-translator": "Each target language is its own column when you translate a sheet. The text is sent to a translation service. Do not paste passwords. Read a sentence you know before you trust a column of product names.",
        "speech-to-text": "The transcript follows the microphone. Names and jargon are the words it misses. Edit those. The audio is not stored as a recording unless the page says it is.",
        "reading-time-calculator": "Time is words divided by the words per minute you set. 250 words at 200 words per minute is a bit over a minute. Speaking time is slower than silent reading if the page offers both.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. Paste a short sample whose answer you can check by eye, then paste the real text.")
    return (
        "Paste the text you want changed. The box is the whole input.",
        detail,
        "For a transform, run it and spot one line. For a count, count one sentence yourself and compare.",
        f"{name} sees the text in the box. It does not open a file on your computer until you paste or upload.",
    )


def dev_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "json-formatter": "Valid JSON uses double quotes and no trailing comma. The formatter only reprints it. A red error is a syntax problem, and the position is the place to look.",
        "json-validator": "Validation tells you the first place the text stops being JSON. Fix that, then validate again. It does not check whether the keys match your API.",
        "json-to-csv": "A CSV is a flat table. Nested objects need a rule for column names, often dotted paths. An array of objects with the same keys becomes one row each.",
        "csv-to-json": "The first row is usually the header. A missing cell shifts every later column. Open the JSON and check one row against the source line.",
        "base64-encoder-decoder": "Base64 is a way to write bytes as text. Encoding 'hi' is not encryption. Decoding fails when the string was wrapped or lost its padding.",
        "jwt-decoder": "A JWT is three Base64 parts: header, payload, and signature. Decoding shows the payload. It does not prove the signature is valid. Anyone can edit the payload of an undecoded token.",
        "timestamp-converter": "Unix time is seconds since 1970-01-01 UTC, unless the field says milliseconds. A 13-digit number is milliseconds. A 10-digit number is seconds. The human date should be in the time zone the page names.",
        "uuid-generator": "A v4 UUID is random. It is not a hash of your input. Generate two. They should not match.",
        "cron-expression-generator": "Five fields are minute, hour, day of month, month, day of week. A leading star is 'every.' The next-run list is the way to check you did not ask for midnight when you wanted noon.",
        "chmod-calculator": "The three digits are owner, group, and others. 7 is read+write+execute (4+2+1). 755 is rwxr-xr-x. The symbolic form and the number should describe the same bits.",
        "px-to-rem-converter": "rem is the root font size. At a 16 px root, 16 px is 1 rem and 24 px is 1.5 rem. Change the root and every rem value moves.",
        "json-diff-checker": "A changed path is a key whose value differs. An added path is only on the right. Order of keys in an object does not matter. Order in an array does.",
        "iban-validator": "The IBAN check is the mod-97 remainder. A valid checksum is not proof the account exists. It is proof the characters are internally consistent for that country's length.",
        "pomodoro-timer": "A classic Pomodoro is 25 minutes of work and a 5 minute break, with a longer break after several rounds. The timer on the page is the clock. It does not block other sites.",
        "regex-tester": "The pattern is the expression. The sample is the text. A match highlight shows what the pattern actually caught, which is often wider than you meant because a dot matches almost anything.",
        "ip-subnet-calculator": "A CIDR such as 192.168.1.10/24 covers 192.168.1.0 through 192.168.1.255, with the first and last addresses reserved as network and broadcast. Usable hosts are the ones in between.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. Feed it a small valid sample and a sample you know is broken. The valid one should succeed and the broken one should point at the problem.")
    return (
        "Paste a real snippet, not a description of the snippet, unless the tool asks you to describe one.",
        detail,
        "Diff the output against the input for a formatter. For a generator, run the result in the real tool that will consume it.",
        f"{name} does not see your repository, your server, or the version of the library on your machine.",
    )


def security_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "password-generator": "Length matters more than a symbol. A 16 character password from a large alphabet is stronger than an 8 character password with a forced symbol. Generate it here, store it in a password manager, and do not reuse it.",
        "password-strength-checker": "The crack-time figure assumes an attacker model and a hashing cost. It is a comparison, not a promise. A password that appears in a known leak is weak even if it looks random.",
        "bcrypt-generator": "Bcrypt has a cost factor, the rounds. Higher rounds are slower and harder to brute force. The hash includes a salt. Verifying should succeed only with the same password.",
        "argon2-hash-generator": "Argon2id is a password hash with memory, time, and parallelism settings. The hash string includes those settings. Verification uses them. Do not invent a shorter hash and call it Argon2.",
        "totp-generator": "A TOTP code is 6 digits from a shared secret and the current 30 second window. The same secret in an authenticator app should show the same code if the clocks match. This is for a secret you are allowed to test.",
        "jwt-verifier": "Verification checks the signature against the secret you provide. A token that decodes but fails verification has been altered or signed with a different key. Decoding alone is not verification.",
        "aes-encrypt-decrypt": "AES-GCM needs the same passphrase to decrypt. A wrong passphrase fails. It does not 'almost' decrypt. The work stays in the browser on this page.",
        "password-entropy-calculator": "Entropy in bits is the size of the random space if the password was chosen at random. A phrase you made up is not that random. The number assumes the method the form describes.",
        "hash-identifier": "A hash length is a clue, not a proof. MD5 is 32 hex characters, SHA-1 is 40, SHA-256 is 64. Several algorithms share a length. The page names the likely ones.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. Treat the output as a secret if it is a password, a key, or a token. Copy it to a manager and clear the box.")
    return (
        "Type the value in the form. Do not use a real password as a test on any tool that sends data to a server.",
        detail,
        "For a hash, change one character of the input. The digest should change completely. For a generator, generate twice and expect two different outputs.",
        f"{name} performs the operation on this page. It does not audit an account or a server.",
    )


def seo_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "utm-builder": "A UTM link is the page URL plus utm_source, utm_medium, and utm_campaign. Source is where the click came from, medium is the channel type, campaign is the effort. The same names, spelled the same way, are what keep a report together.",
        "robots-txt-generator": "A disallow rule blocks crawling of a path. It does not remove a page already indexed. Test the path you care about against the file before you upload it to the site root.",
        "canonical-tag-generator": "The canonical URL is the one you want indexed when several URLs show the same page. It should be absolute, and it should be a page that returns the same content.",
        "hreflang-tag-generator": "Each alternate needs a language, and a region if you mean one, plus the URL of that version. The set should include a self reference. Codes are BCP 47, such as en or en-GB.",
        "serp-snippet-preview": "The pixel width of a title, not only the character count, decides what gets cut off. A wide letter such as W costs more than an i. Rewrite until the title you need is visible.",
        "ads-txt-generator": "An ads.txt line names the ad system, your publisher id, DIRECT or RESELLER, and a certification id. For Google the system is google.com. Upload the file at the root of the domain that serves the ads.",
        "schema-markup-generator": "JSON-LD is a script tag with a type such as Article or FAQPage. The required fields depend on the type. Validate it before you ship it. Markup does not create a review you did not write.",
        "keyword-density-checker": "Density is how often a phrase appears, divided by the length of the text. A high density is not a ranking method. Use it to see if a paragraph repeats a phrase until it sounds unnatural.",
        "redirect-checker": "Each hop has a status, usually 301 or 302, and a target. A chain longer than one hop wastes the crawl. The final URL should be the one you meant to publish.",
        "readability-checker": "Flesch reading ease scores shorter sentences and shorter words as easier. It does not know whether the facts are right. A simple sentence can still be false.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. Use a real URL or a real draft. A made-up example only describes the example.")
    return (
        "Bring the URL, the HTML, or the keyword list the form asks for.",
        detail,
        "Open the real page source or Search Console and confirm the change landed. A result on this page is not a ranking.",
        f"{name} does not control a search engine. It prepares or checks the input you gave it.",
    )


def social_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "twitter-character-counter": "The public limit is 280. A URL in a post is counted as a shortened length, not as the raw number of characters, on the real network. This counter follows the weighted rules it states. Read the number before you post.",
        "instagram-line-break-generator": "Instagram collapses normal line breaks in some fields. The invisible characters this page inserts keep a blank line. Paste into Instagram and look at the preview, because the app can still change spacing.",
        "whatsapp-link-generator": "A wa.me link is https://wa.me/ then the country code and number, with no plus sign and no leading zero, then an optional text query. Test it on your own phone.",
        "hashtag-counter": "Count the tags before you post. Instagram in particular gets noisy and can limit reach when a caption is a wall of tags. The number on the page is the count in the text you pasted.",
        "youtube-tag-extractor": "Tags come from the video page. A video with no public tags returns little. This does not change the video.",
        "social-media-image-sizes": "Each placement has a pixel size. A feed post, a story, and a thumbnail are different rectangles. Export at that size rather than cropping in the app at the last second.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. The preview matches the text you typed. Read it once as a stranger would.")
    return (
        "Paste the caption, the size, or the mockup text you actually plan to publish.",
        detail,
        "Check the character count and the line breaks in the preview. Then paste into the network and look again. The network can still wrap differently.",
        f"{name} does not post for you. A mockup is a picture, not a live post.",
    )


def freelance_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "rate-calculator": "A sustainable hourly rate covers your income goal, your expenses, and the hours you can actually bill. Billable hours are lower than hours worked. Divide the yearly need by the billable hours.",
        "quote-calculator": "A quote is hours times rate, plus expenses, plus the margin you set. The client sees the total. You should still be able to see the cost underneath.",
        "break-even-calculator": "Break-even is the point where revenue covers fixed costs. In hours, it is fixed costs divided by the amount you keep from one hour. Below that, the month loses money.",
        "late-fee-calculator": "A flat fee is a fixed amount. A monthly percent is the percent times the overdue balance times the months. Read which one you selected. A contract has to allow the fee before you send it.",
        "self-employment-tax-calculator": "US self-employment tax and a Pakistan income-tax estimate are different systems. Pick the one the form is set to. This is planning math, not a filing.",
        "contract-generator": "The document is a draft: scope, payment, intellectual property, and confidentiality. Your client's country and a lawyer decide whether a clause holds. Read every blank before you export the PDF.",
        "nda-generator": "A one-way NDA binds one side. A mutual NDA binds both. The names and the definition of confidential information have to match the real project.",
        "change-order-generator": "A change order records work that was not in the original scope, with the added cost and time. Send it before you do the work if you want it to protect you.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. Put in the numbers and the names from the real job, not a sample, before you export.")
    return (
        "Use the figures you and the client already discussed. A blank you leave in will be blank on the PDF.",
        detail,
        "Read the export from top to bottom, including the total and the dates. Then send it.",
        f"{name} drafts the document or the number. It is not your lawyer, your accountant, or the client's acceptance.",
    )


def ai_note(slug: str, name: str, desc: str) -> tuple[str, str, str, str]:
    bits = {
        "code-explainer": "Paste the function, not a description of it. Ask for a beginner or an expert pass depending on who will read the explanation. A bug flag is a hypothesis. Run the code.",
        "sql-query-generator": "Name the tables and the columns in the prompt. Say which database. Read the query, then run it on a copy of the data. A confident explanation can still join the wrong table.",
        "error-diagnoser": "Paste the stack trace and the lines around it. The suggested diff is a starting patch. Apply it only if you understand the line it changes.",
        "ats-resume-checker": "The checker compares your file with the job text you paste. Keyword match is not a hire. A missing heading or a text box in the PDF can make a real skill invisible to the parser.",
        "cover-letter-generator": "The letter is only as specific as the job post and the background you paste. Delete any sentence that claims a skill you do not have.",
        "cron-explainer": "A cron expression is minute, hour, day of month, month, and day of week. The next-run list is in the time zone you select. 'Every day at 9' that shows 09:00 UTC is not 09:00 in Karachi.",
        "video-script-studio": "The script and the shot list come from the video you upload. Watch the source while you read the script. A clean paragraph can skip a line you said.",
        "text-to-speech": "Pick the voice and the tone, then listen to one sentence with a name in it. Export captions only after the words match. Device voices and studio voices are different engines.",
        "online-video-editor": "Trims, captions, and the export run in the browser. The export is a new file. Keep the original clips until you have watched the export.",
    }
    detail = bits.get(slug, f"{desc.rstrip('.')}. The draft follows the text you supplied. A short label is a weak brief.")
    server = "This tool sends the input to a server so a model can run. Do not paste passwords, keys, or a client's secrets. The free plan has a daily limit."
    if tool_is_local(slug):
        server = "This one runs in the browser. The file stays on your device."
    return (
        "Bring the real source: the code, the job post, the diff, or the file.",
        detail,
        "Check names, numbers, and any line you would ship. Change one instruction and see whether the draft follows it.",
        server,
    )


def tool_is_local(slug: str) -> bool:
    return slug in {"online-video-editor", "text-to-speech"}


def generic_note(name: str, desc: str) -> tuple[str, str, str, str]:
    job = desc.rstrip(".")
    return (
        f"Collect the input the page is built for: {lower_first(job)}.",
        f"Run {name} on a small case you can check another way. Write down the result. Change one input and run it again. The line that moves is the part of the job this page owns.",
        f"The result is ready to use when it matches this promise: {job}. If it produced a different kind of answer, this is the wrong tool.",
        f"{name} stops at that promise. It does not apply a rule the page never states.",
    )


def article(tool: dict, related: list[dict]) -> str:
    name = tool["name"]
    desc = tool["description"].strip().rstrip(".")
    href = f"/{tool['category']}/{tool['slug']}"
    bring, example, check, stop = explain(tool)
    privacy = (
        f"{name} runs in your browser. The file or the figures stay on your device."
        if tool.get("clientSide", True)
        else f"{name} sends the input to a server so the work can run. Do not include passwords or account numbers. The free plan has a daily limit."
    )
    lines = [
        f"[{name}]({href}) is the tool for one job: {lower_first(desc)}. This guide covers the inputs to gather, one pass you can check, and the point where the result stops being enough.",
        "",
        f"## What to bring to the {name}",
        "",
        bring,
        "",
        privacy,
        "",
        f"## A worked pass with the {name}",
        "",
        example,
        "",
        "Do that pass with a case you already understand. Then replace it with the real case. Changing one input at a time is how you see which field actually moved the result.",
        "",
        "## How to check the result",
        "",
        check,
        "",
        f"## Where the {name} stops",
        "",
        stop,
        "",
        "If your decision depends on a rule this page does not mention, a lender, a clinic, a teacher, a client, or the vendor of the file, use their rule. Keep this result as the draft you compare against that rule.",
        "",
        "## Questions",
        "",
        f"### What does the {name} do?",
        "",
        f"It is there to {lower_first(desc)}. The form on the [{name}]({href}) page is the place you do that.",
        "",
        f"### How do I know the {name} result is usable?",
        "",
        check,
        "",
        f"### What should I not trust the {name} to decide?",
        "",
        stop,
        "",
    ]
    if related:
        lines += ["## When the next step is a different tool", ""]
        for item in related:
            lines.append(
                f"- [{item['name']}]({item['href']}) — {item['description'].rstrip('.')}."
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def rewrite(raw: str, tools: dict[str, dict]) -> str | None:
    if TEMPLATE_A not in raw or TEMPLATE_B not in raw:
        return None
    data, related_keys, _body = parse_frontmatter(raw)
    if not related_keys:
        return None
    tool = tools.get(related_keys[0])
    if not tool:
        return None
    related = []
    for key in related_keys[1:4]:
        item = tools.get(key)
        if not item:
            continue
        related.append(
            {
                "name": item["name"],
                "href": f"/{item['category']}/{item['slug']}",
                "description": item["description"],
            }
        )
    body = article(tool, related)
    excerpt = f"{tool['description'].rstrip('.')}. What to enter, how to check the result, and where it stops."
    excerpt = excerpt[:220]
    meta = excerpt[:160]
    data["excerpt"] = excerpt
    data["metaDescription"] = meta
    data["updatedDate"] = "2026-10-23"
    order = [
        "title",
        "slug",
        "category",
        "excerpt",
        "publishedDate",
        "updatedDate",
        "featuredImage",
        "author",
        "metaDescription",
    ]
    fm = ["---"]
    for key in order:
        if key in data:
            fm.append(f"{key}: {yaml_quote(data[key])}")
    fm.append("relatedToolSlugs:")
    for key in related_keys:
        fm.append(f"  - {key}")
    fm.append("---")
    return "\n".join(fm) + "\n\n" + body


def main() -> None:
    tools = load_tools()
    changed = 0
    skipped = 0
    for path in sorted(BLOG.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        raw = path.read_text()
        updated = rewrite(raw, tools)
        if updated is None:
            skipped += 1
            continue
        if TEMPLATE_A in updated or TEMPLATE_B in updated:
            raise SystemExit(f"template phrase survived in {path.name}")
        path.write_text(updated)
        changed += 1
    print(f"rewrote {changed}, left {skipped}")


if __name__ == "__main__":
    main()
