export type SemanticTool = {
  name: string;
  slug: string;
  description: string;
  categorySlug: string;
  categoryName: string;
  tagline: string;
  clientSide: boolean;
  related: { name: string; href: string }[];
};

export type SemanticSection = {
  heading: string;
  paragraphs: string[];
};

type Angle = {
  when: string;
  input: string;
  read: string;
  limit: string;
  example?: string;
};

const ANGLES: Record<string, Angle> = {
  "ai-tools": {
    when: "Use it when you already have the source material — code, a job post, an error, or a rough brief — and you want a first draft in plain language.",
    input: "Paste the real text. A short label is not enough for the model to stay on the job described above.",
    read: "Treat the output as a draft. Check names, numbers, and any claim you would send to someone else.",
    limit: "The model can miss context that was not in the box. It does not replace a review by the person who owns the work.",
  },
  "handwriting-ocr": {
    when: "Use it when the words exist on paper or in a photo and you need them as text you can edit.",
    input: "Upload a clear photo of the page. Crop extra background if the writing is small.",
    read: "Compare the text with the photo before you translate, summarize, or paste it into a document.",
    limit: "Blur, glare, and unusual handwriting produce gaps. A gap is a place to look at the photo again, not a fact.",
  },
  "freelancer-tools": {
    when: "Use it when a client conversation needs a number, a clause, or a message you can send the same day.",
    input: "Enter the rate, the dates, and the scope you have actually agreed. Leave a field blank only if you do not have that figure yet.",
    read: "Read the result as a draft you can edit. Your contract and your local rules still decide what you can charge and what you must write.",
    limit: "The page does not know your client’s country, tax status, or the deal you made on a call.",
  },
  "devops-tools": {
    when: "Use it when you need a config, a manifest, or a check you can paste into a repo and then read yourself.",
    input: "Type the names, ports, and versions from the project you are working on. Example values are not your production values.",
    read: "Read the generated file before you apply it. A valid shape can still point at the wrong host or the wrong port.",
    limit: "This does not deploy anything and it does not see your cluster. You copy the result into your own toolchain.",
  },
  "health-tools": {
    when: "Use it when you want a personal estimate from the measurements you have today.",
    input: "Enter height, weight, age, or the other measures the form asks for, in the units printed on the label.",
    read: "Read the result next to the formula the page names. A different formula, or a clinician, can land on a different number.",
    limit: "This is not a diagnosis, a diet, or a training plan. It does not know injuries, medicine, or lab results you did not type.",
  },
  "text-tools": {
    when: "Use it when the text is already in front of you and you need a count, a cleanup, or a different shape.",
    input: "Paste the passage you want changed. The tool only sees that box.",
    read: "Scan the output against the original. A formatter can move line breaks even when the words stay the same.",
    limit: "It does not open a file on your computer until you paste or upload, and it does not guess text you left out.",
  },
  "developer-tools": {
    when: "Use it when a snippet, a payload, or a number needs a format you can paste back into code.",
    input: "Paste valid input for the job in the description. An error line usually means the text is not in that shape yet.",
    read: "Diff the result against what you pasted. Formatting can be right while the data is still the data you typed.",
    limit: "The page does not run your project, call your API, or know the version of the library on your machine.",
  },
  "security-password-tools": {
    when: "Use it when you need a password, a hash, or a check that should not leave the browser.",
    input: "Type the value in the form. Do not reuse a real password as a test if the page says the work is sent to a server.",
    read: "Copy the result into a password manager or the field that asked for it, then clear the box.",
    limit: "A hash or a generator here does not prove an account is secure. It only does the operation in the description.",
  },
  "pdf-tools": {
    when: "Use it when you already have the PDF, or the pages, and you need the file changed in the way the description says.",
    input: "Upload the file and set the page order or the range before you run it.",
    read: "Open the download and check the pages you cared about: order, rotation, and whether the text is still selectable.",
    limit: "A scan stays a picture unless the tool says it reads text. Compression can make images inside the PDF softer.",
  },
  "image-tools": {
    when: "Use it when you have the picture and you need a different size, format, or crop.",
    input: "Upload the original, not a screenshot of a screenshot, if you still have it.",
    read: "Look at the edges and the file size of the download. Smaller files throw away detail on purpose.",
    limit: "The page cannot recover pixels that were never in the file you uploaded.",
  },
  "color-tools": {
    when: "Use it when you have a color, a palette, or a contrast pair and you need the other form of that color.",
    input: "Enter the hex, the RGB, or the two colors the form asks for. A name like “blue” is not a value.",
    read: "Check the converted value in the place you will use it. A contrast ratio is about those two colors, not about a whole page.",
    limit: "Screen settings and surrounding colors change what people see. The number is the math for the values you typed.",
  },
  calculators: {
    when: "Use it when you already have the inputs named in the description and you want that result on one page.",
    input: "Type each figure into the field that names it, in the unit printed on the label.",
    read: "Change one input and see which line moves before you copy the number.",
    limit: "The page only applies the rule in the description. A clinic, a school, a lender, or a tax office may use a different rule.",
  },
  "unit-converters": {
    when: "Use it when you have a measurement in one unit and you need the same measurement in another.",
    input: "Pick the pair the form shows, then type the quantity. The unit on the label is part of the answer.",
    read: "Read both sides. A rounded display can hide a fraction you still need.",
    limit: "It converts the units it lists. It does not know which unit your drawing or your recipe required.",
  },
  "seo-web-tools": {
    when: "Use it when you have a URL, a keyword, or a draft and you need the check described on this page.",
    input: "Paste the real URL or the real draft. A made-up example will not describe your site.",
    read: "Use the result as a list of things to verify in the page source or in Search Console, not as a ranking promise.",
    limit: "The tool does not control Google, and a score here is not a position in search results.",
  },
  "social-media-tools": {
    when: "Use it when you are drafting a post and you need the caption, the count, or the mockup this page builds.",
    input: "Paste the caption or the size you plan to publish. The preview matches that input.",
    read: "Read the caption out loud and check the character count for the network you picked.",
    limit: "It does not post for you, and each network can change its limit after this page was written.",
  },
  "content-creator-tools": {
    when: "Use it when you have footage notes, a script, or audio and you need the next piece of the edit.",
    input: "Bring the source the description names: a video, a transcript, or a short brief.",
    read: "Play or read the result against the source. A clean export can still drop a word you needed.",
    limit: "Browser tools keep the file on your device. A tool that says it uses a server sends that input out, and the free plan has a daily cap.",
  },
  "converters-generators": {
    when: "Use it when you have data in one shape and you need the other shape named in the description.",
    input: "Paste a sample that matches the format. Fix the first error the tool reports before you convert a large file.",
    read: "Open the output in the program that will consume it. A file that looks right in the browser can still miss a column.",
    limit: "The converter follows the rules on this page. It does not invent columns that were not in the input.",
  },
  "home-trade-calculators": {
    when: "Use it when you are about to buy material, size a wire, or price a job and you have the measurements.",
    input: "Enter length, area, or load in the units on the label. A foot typed into a metre box will order the wrong amount.",
    read: "Round up for material you cannot buy in fractions, and keep a waste margin the page does not invent for you.",
    limit: "Codes, span tables, and the product you buy can require a stricter number than this estimate. This page does not replace a licensed tradesperson where the work can injure someone.",
  },
};

const TOOL_ANGLES: Record<string, Angle> = {
  "social-media-tools/small-text-generator": { when:"Use it for a short decorative label, not long paragraphs or essential instructions.", input:"Start with a few words, compare styles, then paste the result into a draft of the destination app.", read:"Preview the characters on a phone and in the app where they will appear.", limit:"These are Unicode substitutions, not a real font-size change. Search and screen-reader output may differ.", example:"For a profile label such as “design notes”, style just those words and keep contact details in plain text." },
  "social-media-tools/linkedin-text-formatter": { when:"Use it to emphasize one short heading or takeaway, not to turn the whole post into decorative characters.", input:"Draft the post in plain text first, then convert only the phrase that should stand out.", read:"Preview the post on desktop and mobile and make sure it is clear without visual styling.", limit:"Unicode lookalikes are not semantic bold or italic. Character counting and screen-reader output may differ.", example:"Style “Three lessons from our launch” and leave the lessons in ordinary text." },
  "pdf-tools/jpg-to-pdf": { when:"Use it when several image files need to be delivered as one PDF, such as receipts, scans, or photographed forms.", input:"Choose the images, check their reading order, and use originals rather than screenshots of compressed images.", read:"Open the exported PDF separately and inspect page order, orientation, and small text.", limit:"Image-to-PDF conversion does not automatically make photographed text searchable; OCR is separate.", example:"For three reimbursement receipts, arrange them by date and check that every total is legible." },
  "security-password-tools/ntlm-hash-generator": { when:"Use it only for learning or authorized legacy-system testing with synthetic input.", input:"Enter a made-up test string and compare the result with a known test vector or controlled lab exercise.", read:"The same input and algorithm should produce the same hash; that is a consistency check, not proof of password strength.", limit:"NTLM is a legacy authentication format. A hash is not encryption and may itself be sensitive credential material.", example:"Run the same synthetic phrase twice, then change one character and compare the output. Never use a production credential." },
  "social-media-tools/instagram-font-generator": { when:"Use it for a short decorative label in a bio or caption that can be checked in the destination app.", input:"Write the bio in plain text first, style one short phrase, then preview it on a phone.", read:"Check legibility at profile size and keep essential details in ordinary text.", limit:"The output uses Unicode lookalikes rather than an installed font; some glyphs may not render or be read aloud as expected.", example:"Style “travel notes” as a short heading, but leave the profile description and contact details plain." },
  "image-tools/gif-maker": { when:"Use it for a short loop or step-by-step sequence where still images communicate the motion.", input:"Choose frames from the same sequence and check their order before exporting.", read:"Watch the downloaded GIF at its intended size and look for flicker or abrupt jumps.", limit:"GIF’s limited color palette can create dithering in photos and gradients; many large frames can create a large file.", example:"For a four-step tutorial, order frames as before, action, after, result; reduce dimensions if the file is too large." },
  "image-tools/webp-to-jpg": { when:"Use it when an upload form or older application specifically requires JPG rather than WebP.", input:"Keep the original, convert the image, then inspect the saved JPG at full size.", read:"Check edges, small text, dimensions, file size, and any transparent area that now has a background.", limit:"JPG is lossy and does not support transparency. Conversion cannot restore detail missing from the original.", example:"For a photo rejected because it is WebP, convert it and confirm the background and edges still look correct." },
  "image-tools/image-to-base64": { when:"Use it when a small image must be represented as text in a data URI or test fixture.", input:"Start with a small icon and check whether the destination expects the full data URI or only the Base64 payload.", read:"Paste the output into a test page or application you control and confirm the image displays.", limit:"Base64 is an encoding, not encryption, and increases raw data size by roughly one third before overhead.", example:"A small interface icon may suit a data URI; a large photo is usually easier to manage as a separate file." },
  "unit-converters/density-converter": { when:"Use it when a datasheet or calculation expresses density in a different unit from the one your project needs.", input:"Read the value and unit together, choose source and target units, and enter the quantity.", read:"Check the magnitude against a known reference and copy the target unit along with the number.", limit:"The converter changes units; it does not identify a material or determine its actual density.", example:"1 g/cm³ equals 1,000 kg/m³, so 800 kg/m³ corresponds to 0.8 g/cm³." },
  "image-tools/add-watermark-to-image": { when:"Use it to add visible attribution or branding before publishing or sending an image.", input:"Keep an untouched original, add the text or logo, and test placement on light and dark backgrounds.", read:"Check that the mark is legible but does not cover a face, product detail, or essential information.", limit:"A visible watermark is not access control; it cannot prevent screenshots, cropping, or deliberate removal.", example:"For product photos, place the mark consistently while keeping labels and product features unobstructed." },
  "home-trade-calculators/budget-calculator": { when:"Use it to compare take-home income with planned expenses for the same period and see what remains.", input:"Use net income, group regular bills, and include a monthly allowance for irregular costs where possible.", read:"Check that all amounts use the same period and compare the leftover amount with actual spending after a month.", limit:"The result is only as complete as the figures entered; it is a planning estimate, not a bank statement.", example:"With $3,000 take-home income and $2,480 of entered expenses, the leftover is $520, about 17.3% of income. These figures are illustrative." },
  "pdf-tools/extract-pdf-pages": { when:"Use it when a recipient needs only selected pages from a longer PDF, such as a chapter, schedule, or receipts.", input:"Identify the pages in the source PDF and remember printed page numbers may differ from physical positions.", read:"Open the extracted PDF and verify first page, last page, order, and orientation before sharing.", limit:"Extracting pages is not the same as redacting sensitive information or cleaning hidden metadata.", example:"When extracting a signature page and two schedules from a contract, check that each schedule retains the pages needed to understand it." },
};

function angleFor(tool: SemanticTool): Angle {
  return (
    TOOL_ANGLES[`${tool.categorySlug}/${tool.slug}`] ??
    ANGLES[tool.categorySlug] ?? {
      when: "Use it when the job in the description is the job you have right now.",
      input: "Enter the text, the file, or the numbers the form asks for.",
      read: "Read the result next to the labels before you copy it.",
      limit: "If the description does not mention your case, this is the wrong page.",
    }
  );
}

const NOT_A_VERB = new Set([
  "full-function",
  "digital",
  "interactive",
  "ai",
  "ai-written",
  "soft-check",
  "free",
  "dedicated",
  "searchable",
  "reference",
]);

function described(description: string) {
  const full = description.trim().replace(/\s+/g, " ").replace(/\.$/, "");
  const first = full.split(/\s+/)[0]?.toLowerCase() ?? "";
  const verb = full.length > 0 && !NOT_A_VERB.has(first);
  const rest = full ? full.charAt(0).toLowerCase() + full.slice(1) : "do the job named in the title";
  return { full, verb, rest };
}

/** First sentence, grammatical for both “Calculate …” and “Full-function …” descriptions. */
export function semanticLead(name: string, description: string): string {
  const d = described(description);
  if (!d.verb) return `The ${name} is a free online tool: ${d.rest}.`;
  return `Use the free ${name} to ${d.rest}.`;
}

function privacy(tool: SemanticTool): string {
  if (tool.clientSide) {
    return `${tool.name} runs in your browser. The file or the figures stay on your device, and the free plan does not ask you to create an account.`;
  }
  return `${tool.name} sends the input to a server so the model can run. The free plan includes a small daily limit. Do not paste passwords or account numbers.`;
}

function relatedSentence(tool: SemanticTool): string {
  if (!tool.related.length) {
    return `Other tools in ${tool.categoryName} sit on that category page when the next step is a different job.`;
  }
  const names = tool.related.map((item) => item.name);
  const list =
    names.length === 1 ? names[0] : `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
  return `Other tools in ${tool.categoryName} include ${list}. Open the one whose description matches the next job.`;
}

/** On-page copy aimed at the tool name as the search phrase, using that tool's description as the scope. */
export function semanticSections(tool: SemanticTool): SemanticSection[] {
  const angle = angleFor(tool);
  return [
    {
      heading: `What the ${tool.name} does`,
      paragraphs: [
        semanticLead(tool.name, tool.description),
        privacy(tool),
      ],
    },
    {
      heading: `When a ${tool.name} is the right page`,
      paragraphs: [
        angle.when,
        `If you are unsure whether this is the right tool, test a small sample first and compare it with the output you expect.`,
      ],
    },
    {
      heading: `How to use the ${tool.name}`,
      paragraphs: [
        angle.input,
        `For a second case, change one input at a time. That makes it easier to spot a unit, formatting, or selection mistake.`,
      ],
    },
    ...(angle.example ? [{ heading: `Example: ${tool.name}`, paragraphs: [angle.example] }] : []),
    {
      heading: "How to read the result",
      paragraphs: [
        angle.read,
        `Check the output in the place you plan to use it—open the exported file, preview the pasted text, or compare the number with a known reference when one is available.`,
      ],
    },
    {
      heading: `What the ${tool.name} leaves out`,
      paragraphs: [
        angle.limit,
        `Do not infer extra features from the name alone. If your task depends on a rule or format not stated here, verify that requirement before you rely on the result.`,
      ],
    },
    {
      heading: "The next tool",
      paragraphs: [relatedSentence(tool)],
    },
  ];
}

export function semanticAboutParagraphs(tool: SemanticTool): string[] {
  return semanticSections(tool).flatMap((section) => section.paragraphs);
}

function mdEscape(text: string): string {
  return text.replace(/\|/g, "\\|");
}

/** Long-form guide for the blog. Same facts as the tool page, with headings a reader can scan. */
export function semanticBlogMarkdown(tool: SemanticTool): string {
  const sections = semanticSections(tool);
  const lines: string[] = [
    `${semanticLead(tool.name, tool.description)} This guide explains that job, how to run it, and what the result does not include. The tool itself is here: [${tool.name}](/${tool.categorySlug}/${tool.slug}).`,
    "",
  ];
  for (const section of sections) {
    lines.push(`## ${section.heading}`, "");
    for (const paragraph of section.paragraphs) lines.push(paragraph, "");
  }
  if (tool.related.length) {
    lines.push("## Run it, then continue", "");
    lines.push(`Use the [${tool.name}](/${tool.categorySlug}/${tool.slug}) for the job above. Related pages:`, "");
    for (const item of tool.related) {
      lines.push(`- [${mdEscape(item.name)}](${item.href})`);
    }
    lines.push("");
  }
  lines.push(
    "## Questions people ask",
    "",
    `### What is a ${tool.name}?`,
    "",
    semanticLead(tool.name, tool.description),
    "",
    `### Is the ${tool.name} free?`,
    "",
    privacy(tool),
    "",
    `### Can I trust the ${tool.name} result on its own?`,
    "",
    `Trust it for the scope in the description: ${tool.description.trim()} If your case depends on a rule this page never states, check that rule before you act on the number or the file.`,
    "",
  );
  return lines.join("\n").trim() + "\n";
}

export function blogCategoryForTool(categorySlug: string, name: string): string {
  if (categorySlug === "health-tools") return "health";
  if (categorySlug === "pdf-tools") return "documents";
  if (categorySlug === "image-tools" || categorySlug === "color-tools" || categorySlug === "social-media-tools") {
    return "photos-design";
  }
  if (categorySlug === "seo-web-tools") return "seo";
  if (categorySlug === "freelancer-tools") return "career";
  if (
    categorySlug === "ai-tools" ||
    categorySlug === "handwriting-ocr" ||
    categorySlug === "content-creator-tools"
  ) {
    return "ai-tech";
  }
  if (
    categorySlug === "developer-tools" ||
    categorySlug === "devops-tools" ||
    categorySlug === "security-password-tools"
  ) {
    return "developer";
  }
  if (categorySlug === "text-tools") return "writing";
  if (categorySlug === "home-trade-calculators") return "home";
  if (categorySlug === "calculators") {
    if (
      /sip|emi|ppf|\bfd\b|epf|nps|loan|mortgage|salary|tax|interest|roi|cagr|xirr|retire|budget|debt|credit|paycheck|invest|gratuity|hra|zakat|inflation|discount|tip/i.test(
        name,
      )
    ) {
      return "personal-finance";
    }
    if (/bmi|calorie|bmr|tdee|body|pregnan|ovulat|due date|sleep|heart|fat/i.test(name)) return "health";
    return "utilities";
  }
  return "utilities";
}
