import { useState } from 'react';

export default function OurWorks() {
  const [selectedCategory, setSelectedCategory] = useState('Все');

  const categories = [
    'Все',
    'BMW',
    'Mercedes',
    'Audi',
    'Ford',
    'Chevrolet',
    'Honda',
    'Toyota',
    'Другие',
  ];

  const works = [
    { id: 1, title: 'BMW 3 Series', category: 'BMW', description: 'Перетяжка салона кожей' },
    { id: 2, title: 'Mercedes E-Class', category: 'Mercedes', description: 'Полная перетяжка + шумоизоляция' },
    { id: 3, title: 'Audi A4', category: 'Audi', description: 'Перетяжка сидений алькантарой' },
    { id: 4, title: 'Ford Focus', category: 'Ford', description: 'Перетяжка руля и сидений' },
    { id: 5, title: 'Chevrolet Cruze', category: 'Chevrolet', description: 'Химчистка + перетяжка' },
    { id: 6, title: 'Honda Civic', category: 'Honda', description: 'Установка спортивных сидений' },
    { id: 7, title: 'BMW X5', category: 'BMW', description: 'Комплексная перетяжка салона' },
    { id: 8, title: 'Mercedes GLE', category: 'Mercedes', description: 'Перетяжка + подсветка' },
    { id: 9, title: 'Audi Q5', category: 'Audi', description: 'Перетяжка дверных карт' },
    { id: 10, title: 'Toyota Camry', category: 'Toyota', description: 'Перетяжка салона экокожей' },
    { id: 11, title: 'Ford Explorer', category: 'Ford', description: 'Полная перетяжка интерьера' },
    { id: 12, title: 'Infiniti QX80', category: 'Другие', description: 'Премиум перетяжка кожей' },
  ];

  const filteredWorks =
    selectedCategory === 'Все'
      ? works
      : works.filter((work) => work.category === selectedCategory);

  return (
    <div className="container mx-auto px-4 py-20">
      <h1 className="text-5xl text-center mb-6 text-white">
        Наши <span className="text-red-700">Работы</span>
      </h1>
      <p className="text-xl text-center text-gray-400 mb-12 max-w-3xl mx-auto">
        Портфолио выполненных работ по тюнингу автомобильных салонов
      </p>

      {/* Category Filter */}
      <div className="flex flex-wrap justify-center gap-3 mb-12">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-6 py-2 rounded-lg transition-all ${
              selectedCategory === category
                ? 'bg-red-700 text-white'
                : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Works Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredWorks.map((work) => (
          <div
            key={work.id}
            className="group bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg overflow-hidden border border-red-900/20 hover:border-red-700/50 transition-all hover:scale-105"
          >
            <div className="h-64 bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center overflow-hidden">
              <img
                src={`https://images.unsplash.com/photo-1599912027667-755b68b4dd3b?w=400&h=300&fit=crop&auto=format&q=80`}
                alt={work.title}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
            </div>
            <div className="p-6">
              <span className="inline-block px-3 py-1 bg-red-700/20 text-red-700 rounded-full text-sm mb-3">
                {work.category}
              </span>
              <h3 className="text-xl mb-2 text-white">{work.title}</h3>
              <p className="text-gray-400">{work.description}</p>
            </div>
          </div>
        ))}
      </div>

      {filteredWorks.length === 0 && (
        <div className="text-center py-20">
          <p className="text-gray-400 text-xl">Работы в этой категории пока отсутствуют</p>
        </div>
      )}
    </div>
  );
}
