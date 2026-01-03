import { Calendar } from 'lucide-react';

export default function NewWorks() {
  const newWorks = [
    {
      id: 1,
      title: 'Porsche Cayenne',
      date: '15 декабря 2025',
      category: 'Премиум перетяжка',
      description: 'Полная перетяжка салона натуральной кожей Nappa с контрастной строчкой. Перфорация на центральных вставках сидений.',
      image: 'https://images.unsplash.com/photo-1599912027667-755b68b4dd3b?w=600&h=400&fit=crop',
    },
    {
      id: 2,
      title: 'BMW X7',
      date: '28 декабря 2025',
      category: 'Комплексная работа',
      description: 'Перетяжка салона + шумоизоляция + установка подсветки. Использовалась экокожа премиум класса.',
      image: 'https://images.unsplash.com/photo-1581116536919-e906d33a4157?w=600&h=400&fit=crop',
    },
    {
      id: 3,
      title: 'Mercedes-Benz GLE',
      date: '2 января 2026',
      category: 'Перетяжка + тюнинг',
      description: 'Установка спортивных сидений с последующей перетяжкой алькантарой. Кастомная подсветка салона.',
      image: 'https://images.unsplash.com/photo-1762933855598-273a51b47649?w=600&h=400&fit=crop',
    },
    {
      id: 4,
      title: 'Audi Q8',
      date: '5 января 2026',
      category: 'Перетяжка руля и сидений',
      description: 'Перетяжка руля перфорированной кожей с красной нитью. Перетяжка передних сидений.',
      image: 'https://images.unsplash.com/photo-1599912027667-755b68b4dd3b?w=600&h=400&fit=crop',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-20">
      <h1 className="text-5xl text-center mb-6 text-white">
        Новые <span className="text-red-700">Работы</span>
      </h1>
      <p className="text-xl text-center text-gray-400 mb-16 max-w-3xl mx-auto">
        Последние проекты нашей студии
      </p>

      <div className="space-y-8">
        {newWorks.map((work) => (
          <div
            key={work.id}
            className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg overflow-hidden border border-red-900/20 hover:border-red-700/50 transition-all"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Image */}
              <div className="h-80 md:h-auto overflow-hidden">
                <img
                  src={work.image}
                  alt={work.title}
                  className="w-full h-full object-cover hover:scale-110 transition-transform duration-500"
                />
              </div>

              {/* Content */}
              <div className="p-8 flex flex-col justify-center">
                <div className="flex items-center gap-3 mb-4">
                  <span className="inline-block px-4 py-1 bg-red-700/20 text-red-700 rounded-full">
                    {work.category}
                  </span>
                  <div className="flex items-center gap-2 text-gray-400">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm">{work.date}</span>
                  </div>
                </div>

                <h2 className="text-3xl mb-4 text-white">{work.title}</h2>
                <p className="text-gray-300 text-lg leading-relaxed">{work.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* More works CTA */}
      <div className="mt-12 text-center">
        <p className="text-gray-400">
          Больше работ в нашей{' '}
          <a href="/our-works" className="text-red-700 hover:text-red-600 underline">
            галерее
          </a>
        </p>
      </div>
    </div>
  );
}
