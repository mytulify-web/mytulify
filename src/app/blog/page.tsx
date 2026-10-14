import type { Metadata } from "next";
import { BlogCategoryNav } from "@/components/blog/BlogCategoryNav";
import { formatPostDate, getIndexablePosts, getBlogCategory, type BlogPost } from "@/lib/blog";
import { site } from "@/lib/site";
import { englishOnlyPageMeta, clampMetaDescription } from "@/lib/seo";
import { getMetadataLocale } from "@/i18n/locale";

function esc(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function postsHtml(posts: BlogPost[]) {
  return posts
    .map(
      (post) =>
        `<a class="post-row" href="/blog/${esc(post.slug)}"><b>${esc(post.title)}</b><small>${esc(formatPostDate(post.publishedDate))} · ${post.readingMinutes} min read · ${esc(post.excerpt)}</small></a>`,
    )
    .join("");
}

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ lang?: string | string[]; category?: string | string[] }>;
}): Promise<Metadata> {
  const sp = await searchParams;
  const locale = await getMetadataLocale(searchParams);
  const categorySlug = typeof sp.category === "string" ? sp.category : undefined;
  const category = getBlogCategory(categorySlug);
  const description = clampMetaDescription(
    category
      ? `${category.description} Practical guides from ${site.name}.`
      : `Original how-tos, comparisons, and practical guides on calculators, developer workflows, PDFs, images, and more.`,
  );
  return englishOnlyPageMeta("/blog", locale, {
    title: category ? `${category.name} · Blog` : "Blog",
    description,
    socialTitle: category ? `${category.name} · ${site.name} Blog` : `Blog · ${site.name}`,
  });
}

export default async function BlogIndexPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string | string[] }>;
}) {
  const sp = await searchParams;
  const categorySlug = typeof sp.category === "string" ? sp.category : undefined;
  const category = getBlogCategory(categorySlug);
  const posts = getIndexablePosts();
  const filtered = category ? posts.filter((p) => p.category === category.slug) : posts;

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
      <div className="max-w-2xl">
        <p className="section-label">Blog</p>
        <h1 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">
          {category ? category.name : "Practical guides and comparisons"}
        </h1>
        <p className="mt-3 text-muted">
          {category
            ? category.description
            : `Original how-tos, comparisons, and practical guides on calculators, developer workflows, PDFs, images, and more.`}
        </p>
      </div>

      <BlogCategoryNav active={category?.slug} />

      {filtered.length === 0 ? (
        <p className="mt-12 text-muted">No posts in this category yet.</p>
      ) : (
        <div className="mt-8" dangerouslySetInnerHTML={{ __html: postsHtml(filtered) }} />
      )}
    </div>
  );
}
