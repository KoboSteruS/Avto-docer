import { ArrowRight, Star, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="relative h-[600px] flex items-center justify-center overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-40"
          style={{ 
            backgroundImage: `url('https://images.unsplash.com/photo-1599912027667-755b68b4dd3b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBjYXIlMjBpbnRlcmlvcnxlbnwxfHx8fDE3NjcyNjQ0NTh8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral')` 
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 to-black/80" />
        
        <div className="container mx-auto px-4 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl mb-6 text-white">
            Студия Автомобильного <br />
            <span className="text-red-700">Интерьера</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Профессиональный тюнинг автомобильного салона в Петрозаводске. 
            Высокое качество, индивидуальный подход к каждому клиенту.
          </p>
          <Link
            to="/services"
            className="inline-flex items-center gap-2 bg-red-700 hover:bg-red-800 transition-colors px-8 py-4 rounded-lg text-lg"
          >
            Наши Услуги
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Services Preview */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-4xl text-center mb-12 text-white">
          Наши <span className="text-red-700">Услуги</span>
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              title: 'Перетяжка Автосалонов',
              description: 'Профессиональная перетяжка сидений, дверных карт, потолка высококачественными материалами',
              image: 'https://images.unsplash.com/photo-1599912027667-755b68b4dd3b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBjYXIlMjBpbnRlcmlvcnxlbnwxfHx8fDE3NjcyNjQ0NTh8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
            },
            {
              title: 'Установка Сигнализации',
              description: 'Установка современных охранных систем с автозапуском и мобильным приложением',
              image: 'https://images.unsplash.com/photo-1762933855598-273a51b47649?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjYXIlMjBkZXRhaWxpbmclMjBzZXJ2aWNlfGVufDF8fHx8MTc2NzM2NzgxMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
            },
            {
              title: 'Шумоизоляция',
              description: 'Комплексная шумоизоляция автомобиля для максимального комфорта',
              image: 'https://images.unsplash.com/photo-1581116536919-e906d33a4157?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjdXN0b20lMjBjYXIlMjBpbnRlcmlvcnxlbnwxfHx8fDE3NjczNjc4MTF8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
            },
          ].map((service, index) => (
            <div
              key={index}
              className="group bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg overflow-hidden border border-red-900/20 hover:border-red-700/50 transition-all hover:scale-105"
            >
              <div className="h-48 overflow-hidden">
                <img
                  src={service.image}
                  alt={service.title}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl mb-3 text-white">{service.title}</h3>
                <p className="text-gray-400">{service.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            to="/services"
            className="inline-flex items-center gap-2 bg-red-700 hover:bg-red-800 transition-colors px-6 py-3 rounded-lg"
          >
            Все Услуги
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="bg-black/40 py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl text-center mb-12 text-white">
            Почему выбирают <span className="text-red-700">нас</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { icon: Star, title: 'Опыт работы', text: 'Более 10 лет на рынке' },
              { icon: CheckCircle, title: 'Качество', text: 'Используем лучшие материалы' },
              { icon: Star, title: 'Гарантия', text: 'Гарантия на все работы' },
              { icon: CheckCircle, title: 'Индивидуальный подход', text: 'К каждому клиенту' },
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-red-700/20 rounded-full mb-4">
                  <item.icon className="w-8 h-8 text-red-700" />
                </div>
                <h3 className="text-xl mb-2 text-white">{item.title}</h3>
                <p className="text-gray-400">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="bg-gradient-to-r from-red-900/30 to-red-700/30 rounded-2xl p-12 text-center border border-red-700/50">
          <h2 className="text-4xl mb-4 text-white">Готовы преобразить свой автомобиль?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Свяжитесь с нами для консультации и расчета стоимости
          </p>
          <Link
            to="/contacts"
            className="inline-flex items-center gap-2 bg-red-700 hover:bg-red-800 transition-colors px-8 py-4 rounded-lg text-lg"
          >
            Связаться с нами
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
