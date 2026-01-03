import { Star, Quote } from 'lucide-react';

export default function Reviews() {
  const reviews = [
    {
      id: 1,
      name: 'Алексей Иванов',
      car: 'BMW X5',
      rating: 5,
      date: '15 ноября 2025',
      text: 'Отличная работа! Перетянули салон моего X5 натуральной кожей. Качество на высшем уровне, все сделано аккуратно и профессионально. Рекомендую!',
    },
    {
      id: 2,
      name: 'Мария Петрова',
      car: 'Mercedes E-Class',
      rating: 5,
      date: '3 декабря 2025',
      text: 'Очень довольна результатом! Сделали полную перетяжку салона и химчистку. Машина преобразилась, как новая. Спасибо большое мастерам!',
    },
    {
      id: 3,
      name: 'Дмитрий Смирнов',
      car: 'Audi A6',
      rating: 5,
      date: '18 декабря 2025',
      text: 'Профессиональный подход к работе. Установили сигнализацию и сделали шумоизоляцию. Все выполнено качественно и в срок. Цены адекватные.',
    },
    {
      id: 4,
      name: 'Сергей Николаев',
      car: 'Toyota Land Cruiser',
      rating: 5,
      date: '7 января 2026',
      text: 'Делал перетяжку руля и сидений. Результат превзошел ожидания! Материалы отличного качества, работа выполнена на совесть. Буду обращаться еще.',
    },
    {
      id: 5,
      name: 'Ольга Васильева',
      car: 'Ford Explorer',
      rating: 5,
      date: '20 декабря 2025',
      text: 'Замечательная студия! Сделали перетяжку салона экокожей. Все очень аккуратно, без косяков. Мастера знают свое дело. Очень рекомендую!',
    },
    {
      id: 6,
      name: 'Андрей Ковалев',
      car: 'Volkswagen Touareg',
      rating: 5,
      date: '29 декабря 2025',
      text: 'Обратился для установки дополнительных сидений и перетяжки. Работа выполнена на отлично! Индивидуальный подход, качественные материалы.',
    },
  ];

  const averageRating = 5;
  const totalReviews = reviews.length;

  return (
    <div className="container mx-auto px-4 py-20">
      <h1 className="text-5xl text-center mb-6 text-white">
        Отзывы <span className="text-red-700">Клиентов</span>
      </h1>
      <p className="text-xl text-center text-gray-400 mb-12 max-w-3xl mx-auto">
        Мнения наших клиентов о качестве работы студии Avto-Декор
      </p>

      {/* Rating Summary */}
      <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-8 border border-red-900/20 mb-12 max-w-md mx-auto">
        <div className="text-center">
          <div className="text-5xl text-white mb-2">{averageRating.toFixed(1)}</div>
          <div className="flex items-center justify-center gap-1 mb-2">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-6 h-6 ${
                  i < averageRating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-600'
                }`}
              />
            ))}
          </div>
          <div className="text-gray-400">На основе {totalReviews} отзывов</div>
        </div>
      </div>

      {/* Reviews Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reviews.map((review) => (
          <div
            key={review.id}
            className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-6 border border-red-900/20 hover:border-red-700/50 transition-all relative"
          >
            <Quote className="absolute top-4 right-4 w-8 h-8 text-red-700/20" />
            
            <div className="flex items-center gap-1 mb-4">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-5 h-5 ${
                    i < review.rating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-600'
                  }`}
                />
              ))}
            </div>

            <p className="text-gray-300 mb-6 leading-relaxed">{review.text}</p>

            <div className="border-t border-gray-700 pt-4">
              <div className="text-white mb-1">{review.name}</div>
              <div className="text-sm text-gray-400">{review.car}</div>
              <div className="text-sm text-gray-500 mt-2">{review.date}</div>
            </div>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="mt-16 bg-gradient-to-r from-red-900/30 to-red-700/30 rounded-2xl p-12 text-center border border-red-700/50">
        <h2 className="text-3xl mb-4 text-white">Станьте нашим клиентом</h2>
        <p className="text-gray-300 mb-6">
          Присоединяйтесь к сотням довольных клиентов студии Avto-Декор
        </p>
        <a
          href="tel:88142282380"
          className="inline-block bg-red-700 hover:bg-red-800 transition-colors px-8 py-4 rounded-lg text-lg"
        >
          Записаться на консультацию
        </a>
      </div>
    </div>
  );
}
