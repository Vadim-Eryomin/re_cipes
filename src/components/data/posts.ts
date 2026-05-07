export interface Post {
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

export const samplePosts: Post[] = [
  {
    id: '1',
    userAvatar: '~/assets/test1.png',
    topic: 'r/pancakes',
    userName: '@mili_Vasya',
    date: '1 дн. назад',
    title: 'Я сделала блины, зацените. Очень быстро и просто готовится. Займет не больше 10 минут. Рецепт моей любимой бабушки',
    image: '~/assets/post1.png',
    likes: 24,
    comments: 12,
    userLiked: false,
    userDisliked: false
  },
  {
    id: '2',
    userAvatar: '~/assets/test2.png',
    topic: 'r/soup',
    userName: '@chef_anton',
    date: '3 ч. назад',
    title: 'Суп за 15 минут. Вкуснее чем в ресторане!',
    image: '~/assets/post2.png',
    likes: -5,
    comments: 3,
    userLiked: false,
    userDisliked: false
  },
  {
    id: '3',
    userAvatar: '~/assets/test3.png',
    topic: 'r/salads',
    userName: '@healthy_eat',
    date: '2 дн. назад',
    title: 'Салат Цезарь по-домашнему. Очень сочно и вкусно!',
    image: '~/assets/post3.png',
    likes: 45,
    comments: 18,
    userLiked: false,
    userDisliked: false
  },
  {
    id: '4',
    userAvatar: '~/assets/test4.png',
    topic: 'r/desserts',
    userName: '@sweet_tooth',
    date: '5 ч. назад',
    title: 'Тирамису без выпечки. Простой рецепт потрясающего десерта',
    image: '~/assets/post4.png',
    likes: 67,
    comments: 23,
    userLiked: false,
    userDisliked: false
  },
  {
    id: '5',
    userAvatar: '~/assets/test5.png',
    topic: 'r/pasta',
    userName: '@italian_cook',
    date: '1 дн. назад',
    title: 'Карбонара по-римски. Настоящий итальянский рецепт',
    image: '~/assets/post5.png',
    likes: 89,
    comments: 34,
    userLiked: false,
    userDisliked: false
  }
];