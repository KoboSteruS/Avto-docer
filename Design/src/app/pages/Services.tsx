import { Car, Volume2, Shield, Sparkles, Settings, Wrench } from 'lucide-react';

export default function Services() {
  const services = [
    {
      icon: Car,
      title: 'Перетяжка Автосалонов',
      description: 'Профессиональная перетяжка салона автомобиля качественными материалами. Мы используем натуральную и экокожу, алькантару, карпет.',
      features: [
        'Перетяжка сидений',
        'Перетяжка дверных карт',
        'Перетяжка потолка',
        'Перетяжка торпеды',
        'Перетяжка руля',
      ],
    },
    {
      icon: Shield,
      title: 'Установка Сигнализации',
      description: 'Установка современных охранных систем с автозапуском, GPS-мониторингом и мобильным приложением.',
      features: [
        'Сигнализация с автозапуском',
        'GPS-трекинг',
        'Мобильное приложение',
        'Защита от угона',
        'Датчики удара и наклона',
      ],
    },
    {
      icon: Volume2,
      title: 'Шумоизоляция',
      description: 'Комплексная шумоизоляция автомобиля для снижения уровня шума и повышения комфорта в салоне.',
      features: [
        'Шумоизоляция дверей',
        'Шумоизоляция пола',
        'Шумоизоляция крыши',
        'Шумоизоляция арок',
        'Виброизоляция',
      ],
    },
    {
      icon: Sparkles,
      title: 'Химчистка Салона',
      description: 'Профессиональная химчистка автомобильного салона с использованием специализированного оборудования.',
      features: [
        'Чистка сидений',
        'Чистка потолка',
        'Чистка ковриков',
        'Очистка пятен',
        'Устранение запахов',
      ],
    },
    {
      icon: Settings,
      title: 'Переоборудование',
      description: 'Переоборудование салона автомобиля под ваши потребности: установка дополнительных сидений, столиков и т.д.',
      features: [
        'Установка дополнительных сидений',
        'Монтаж складных столиков',
        'Переделка багажника',
        'Индивидуальные решения',
      ],
    },
    {
      icon: Wrench,
      title: 'Тюнинг',
      description: 'Тюнинг автомобиля: улучшение характеристик, модификация интерьера и экстерьера.',
      features: [
        'Чип-тюнинг',
        'Спортивные сиденья',
        'Кастомная подсветка',
        'Индивидуальный дизайн',
      ],
    },
  ];

  return (
    <div className="container mx-auto px-4 py-20">
      <h1 className="text-5xl text-center mb-6 text-white">
        Наши <span className="text-red-700">Услуги</span>
      </h1>
      <p className="text-xl text-center text-gray-400 mb-16 max-w-3xl mx-auto">
        Мы предлагаем полный спектр услуг по тюнингу и улучшению автомобильного интерьера
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {services.map((service, index) => (
          <div
            key={index}
            className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-8 border border-red-900/20 hover:border-red-700/50 transition-all"
          >
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0">
                <div className="w-16 h-16 bg-red-700/20 rounded-lg flex items-center justify-center">
                  <service.icon className="w-8 h-8 text-red-700" />
                </div>
              </div>
              
              <div className="flex-1">
                <h2 className="text-2xl mb-3 text-white">{service.title}</h2>
                <p className="text-gray-400 mb-6">{service.description}</p>
                
                <h3 className="text-white mb-3">Включает:</h3>
                <ul className="space-y-2">
                  {service.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-gray-300">
                      <div className="w-1.5 h-1.5 bg-red-700 rounded-full flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="mt-16 bg-gradient-to-r from-red-900/30 to-red-700/30 rounded-2xl p-12 text-center border border-red-700/50">
        <h2 className="text-3xl mb-4 text-white">Нужна консультация?</h2>
        <p className="text-gray-300 mb-6">
          Свяжитесь с нами для подробной консультации и расчета стоимости услуг
        </p>
        <a
          href="tel:88142282380"
          className="inline-block bg-red-700 hover:bg-red-800 transition-colors px-8 py-4 rounded-lg text-lg"
        >
          8(8142) 28-23-80
        </a>
      </div>
    </div>
  );
}
