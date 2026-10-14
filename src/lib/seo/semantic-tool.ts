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

function angleFor(categorySlug: string): Angle {
  return (
    ANGLES[categorySlug] ?? {
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
const VERIFICATION_GUIDANCE: Record<string, string> = {
  "ai-tools": "Compare names, dates, numbers, and claims with the source. Test one prompt that includes an explicit constraint before using the draft.",
  "handwriting-ocr": "Compare names, digits, punctuation, and line breaks with the original image. Treat uncertain characters as items to review, not confirmed text.",
  "freelancer-tools": "Check currency, dates, deliverables, revision counts, payment timing, and applicable local rules before sending or signing anything.",
  "devops-tools": "Validate syntax with the actual CLI or parser, then review environment names, permissions, ports, and secrets before applying a generated config.",
  "health-tools": "Confirm the units and formula used. Do not use a calculator result to diagnose a condition or change medication.",
  "text-tools": "Test punctuation, whitespace, line breaks, and Unicode characters that matter to your task.",
  "developer-tools": "Run the result against a valid sample and a malformed sample. Verify syntax against the version of the language or library in your project.",
  "security-password-tools": "Check the algorithm and settings against your security requirements. Never paste a real password or secret into a server-based tool.",
  "pdf-tools": "Open the downloaded file and check page count, order, orientation, searchable text, and visual quality.",
  "image-tools": "Inspect the downloaded file's dimensions, transparency, crop, compression, and quality at full size.",
  "color-tools": "Check the exact color values and contrast against the actual foreground and background where the colors will appear.",
  calculators: "Check input units, assumptions, rounding, and one result against an independent calculation or an authoritative source.",
  "unit-converters": "Confirm that the source and target units describe the same kind of measurement, and that displayed rounding suits the task.",
  "seo-web-tools": "Verify the live URL, rendered HTML, canonical, and robots directives. A tool result is not a promise that Google will index or rank a page.",
  "social-media-tools": "Check the platform's current limits and preview line breaks, mentions, and formatting before posting.",
  "content-creator-tools": "Compare the output with the source recording or brief, especially names, timestamps, factual claims, and omitted details.",
  "converters-generators": "Validate the output in the program or parser that will consume it; check encoding, delimiters, and required fields.",
  "home-trade-calculators": "Recheck units, load assumptions, waste, local codes, and manufacturer instructions. Use a qualified professional for safety-critical work.",
};

function verificationGuidance(categorySlug: string): string {
  return VERIFICATION_GUIDANCE[categorySlug] ??
    "Compare the output with the input and the requirement you started with. Test an edge case before relying on the result.";
}

/** Page copy uses category-specific verification guidance instead of repeated filler paragraphs. */
export function semanticSections(tool: SemanticTool): SemanticSection[] {
  const angle = angleFor(tool.categorySlug);
  return [
    {
      heading: `What the ${tool.name} does`,
      paragraphs: [
        semanticLead(tool.name, tool.description),
        privacy(tool),
      ],
    },
    {
      heading: `When the ${tool.name} helps`,
      paragraphs: [
        angle.when,
        `Choose this page when its described output matches the decision, file, or check you need. The tool cannot infer requirements that you leave out.`,
      ],
    },
    {
      heading: `How to use the ${tool.name}`,
      paragraphs: [
        angle.input,
        `Start with a small, representative example. Keep the source and result side by side, then change one input at a time so you can tell which setting changed the output.`,
      ],
    },
    {
      heading: "Verify the output",
      paragraphs: [
        angle.read,
        verificationGuidance(tool.categorySlug),
      ],
    },
    {
      heading: `Limits of the ${tool.name}`,
      paragraphs: [
        angle.limit,
      ],
    },
    {
      heading: "Related tools",
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
