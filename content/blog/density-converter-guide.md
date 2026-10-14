---
title: "Density Converter: Convert kg/m3, g/cm3, lb/ft3, and other density units"
slug: density-converter-guide
category: utilities
excerpt: "Convert density measurements between common units and learn how to sanity-check the magnitude before using the result."
publishedDate: 2026-10-01
updatedDate: 2026-10-14
featuredImage: /blog/covers/density-converter-guide.svg
author: Mytulify Team
metaDescription: "A density conversion guide with common unit relationships, worked examples, dimensional checks, and practical cautions."
relatedToolSlugs:
  - unit-converters/density-converter
  - unit-converters/length-converter
  - unit-converters/weight-converter
  - unit-converters/temperature-converter
---

Density is mass divided by volume. A density converter changes the unit used to express that same physical quantity; it does not change the material or measure its density for you. Use the [Density Converter](/unit-converters/density-converter) when a datasheet, lab result, or calculation uses a different unit from the one your project expects.

## Common density units

You may see density expressed in kilograms per cubic metre (kg/m³), grams per cubic centimetre (g/cm³), or pounds per cubic foot (lb/ft³). A useful reference relationship is:

- **1 g/cm³ = 1,000 kg/m³**
- **1 g/cm³ ≈ 62.43 lb/ft³**

These relationships help catch unit mistakes, but they are not a substitute for checking the source value and the unit printed next to it.

## Worked example

Water near ordinary room temperature has a density close to 1 g/cm³, or about 1,000 kg/m³. If a material datasheet lists 800 kg/m³, that is 0.8 g/cm³. The numbers look different because the units differ; the physical density is the same.

## How to convert a value safely

1. Read the source value and unit together.
2. Open the [Density Converter](/unit-converters/density-converter).
3. Select the source and target units shown by the tool.
4. Enter the value and compare the result with an approximate reference value if one is available.
5. Copy the number with its target unit, not the number alone.

## Common mistakes

- **Mixing mass and weight units:** density uses mass per volume. Make sure the input is actually a density, not mass or volume by itself.
- **Dropping the unit label:** 800 kg/m³ and 800 g/cm³ are not remotely the same value.
- **Using an assumed material value:** density changes with composition, temperature, and sometimes pressure. Use the value relevant to your material and conditions.
- **Rounding too early:** keep sufficient precision during intermediate calculations and round to the accuracy the source data supports.

## Frequently asked questions

### Is 1 g/cm³ equal to 1 kg/m³?

No. One gram per cubic centimetre equals 1,000 kilograms per cubic metre.

### Does the converter identify a material?

No. It converts a value you supply; it does not determine which substance you have.

### How many decimal places should I keep?

Keep enough precision for the source measurement and intended use. Extra decimal places do not make an uncertain measurement more accurate.
