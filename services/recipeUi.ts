import { mediaUrl } from './api';

export interface FeedPost {
  id: string;
  userAvatar: string;
  topic: string;
  userName: string;
  date: string;
  title: string;
  image: string;
  likes: number;
  comments: number;
  userLiked: boolean;
  userDisliked: boolean;
}

export interface ProfilePost {
  id: string;
  author: { name: string; avatar_url: string };
  title: string;
  description: string;
  text: string;
  medias: string[];
  created_at: string;
  likes_count: number;
  comments_count: number;
  user_vote: number | null;
}

export function formatRelative(createdAt: string | undefined): string {
  if (!createdAt) return 'недавно';
  const date = new Date(createdAt);
  if (isNaN(date.getTime())) return 'недавно';

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffHours === 0) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return diffMinutes < 1 ? 'только что' : `${diffMinutes} мин назад`;
    }
    return `${diffHours} ч назад`;
  }
  if (diffDays === 1) return '1 дн. назад';
  return `${diffDays} дн. назад`;
}

export function formatDate(createdAt: string | undefined): string {
  if (!createdAt) return '—';
  const date = new Date(createdAt);
  if (isNaN(date.getTime())) return '—';
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
}

export function mapRecipeToFeedPost(recipe: any): FeedPost {
  const vote = recipe.user_vote;
  const authorImage = recipe.author?.image?.url || recipe.author?.image?.path;
  const mainImage = recipe.main_image?.url || recipe.main_image?.path;

  return {
    id: String(recipe.id),
    userAvatar: mediaUrl(authorImage),
    topic: recipe.thread?.title || '',
    userName: `@${recipe.author?.login || 'user'}`,
    date: formatRelative(recipe.created_at),
    title: recipe.title || recipe.description || '',
    image: mediaUrl(mainImage),
    likes: recipe.score ?? 0,
    comments: recipe.comments_count ?? 0,
    userLiked: vote === 1,
    userDisliked: vote === -1,
  };
}

export function mapRecipeToProfilePost(recipe: any): ProfilePost {
  const mainImage = recipe.main_image?.url || recipe.main_image?.path;
  const authorImage = recipe.author?.image?.url || recipe.author?.image?.path;

  return {
    id: String(recipe.id),
    author: {
      name: `@${recipe.author?.login || 'user'}`,
      avatar_url: mediaUrl(authorImage),
    },
    title: recipe.title || 'Без названия',
    description: recipe.description || '',
    text: recipe.description || recipe.title || '',
    medias: mainImage ? [mediaUrl(mainImage)] : [],
    created_at: recipe.created_at,
    likes_count: recipe.score ?? 0,
    comments_count: recipe.comments_count ?? 0,
    user_vote: recipe.user_vote ?? null,
  };
}

export function mapRecipeToDetail(recipe: any) {
  const vote = recipe.user_vote;
  const authorImage = recipe.author?.image?.url || recipe.author?.image?.path;
  const mainImage = recipe.main_image?.url || recipe.main_image?.path;

  return {
    id: String(recipe.id),
    userAvatar: mediaUrl(authorImage),
    topic: recipe.thread?.title || '',
    userName: `@${recipe.author?.login || 'user'}`,
    date: formatRelative(recipe.created_at),
    title: recipe.title || '',
    image: mediaUrl(mainImage),
    likes: recipe.score ?? 0,
    comments: recipe.comments_count ?? (recipe.comments?.length ?? 0),
    userLiked: vote === 1,
    userDisliked: vote === -1,
    ingredients: (recipe.ingredients || []).map((i: any) => ({
      name: i.name,
      quantity: i.quantity,
      unit: i.unit,
    })),
    steps: (recipe.steps || []).map((s: any) => ({
      order: s.order_index,
      description: s.description,
      image: mediaUrl(s.image?.url || s.image?.path),
    })),
  };
}

export function mapCommentToUi(comment: any) {
  const authorImage = comment.author?.image?.url || comment.author?.image?.path;
  return {
    id: String(comment.id),
    user: `@${comment.author?.login || 'user'}`,
    avatar: mediaUrl(authorImage),
    time: formatRelative(comment.created_at),
    text: comment.content,
    parent_id: comment.parent_id ? String(comment.parent_id) : null,
    created_at: comment.created_at,
  };
}

export function buildCommentsTree(flatComments: any[]): any[] {
  const map = new Map<string, any>();
  const roots: any[] = [];

  flatComments.forEach((comment) => {
    map.set(comment.id, { ...comment, replies: [] });
  });

  flatComments.forEach((comment) => {
    const node = map.get(comment.id)!;
    if (comment.parent_id && map.has(comment.parent_id)) {
      map.get(comment.parent_id)!.replies.push(node);
    } else {
      roots.push(node);
    }
  });

  roots.sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  roots.forEach((root) => {
    if (root.replies?.length) {
      root.replies.sort(
        (a: any, b: any) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
    }
  });

  return roots;
}
