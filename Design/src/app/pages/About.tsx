import { Award, Users, Clock, Target } from 'lucide-react';

export default function About() {
  const stats = [
    { icon: Clock, value: '10+', label: 'лет опыта' },
    { icon: Users, value: '500+', label: 'довольных клиентов' },
    { icon: Target, value: '100%', label: 'гарантия качества' },
    { icon: Award, value: '1000+', label: 'выполненных работ' },
  ];

  return (
    <div className="container mx-auto px-4 py-20">
      <h1 className="text-5xl text-center mb-6 text-white">
        О <span className="text-red-700">Студии</span>
      </h1>
      <p className="text-xl text-center text-gray-400 mb-16 max-w-3xl mx-auto">
        Профессиональная студия по тюнингу автомобильного интерьера в Петрозаводске
      </p>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20">
        {/* Image */}
        <div className="rounded-lg overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1672844825476-66737d85bfce?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhdXRvbW90aXZlJTIwd29ya3Nob3B8ZW58MXx8fHwxNzY3MzU1MzExfDA&ixlib=rb-4.1.0&q=80&w=1080"
            alt="Наша студия"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Text Content */}
        <div className="flex flex-col justify-center">
          <h2 className="text-3xl mb-6 text-white">
            Добро пожаловать в <span className="text-red-700">Avto-Декор</span>
          </h2>
          
          <div className="space-y-4 text-gray-300 text-lg leading-relaxed">
            <p>
              Студия Avto-Декор работает на рынке автомобильного тюнинга уже более 10 лет. 
              За это время мы выполнили сотни проектов различной сложности и заслужили доверие 
              наших клиентов.
            </p>
            
            <p>
              Наша команда состоит из высококвалифицированных специалистов, каждый из которых 
              является профессионалом в своей области. Мы используем только качественные 
              материалы от проверенных производителей и современное оборудование.
            </p>
            
            <p>
              Мы гордимся тем, что к нам обращаются владельцы автомобилей премиум-класса, 
              доверяя нам свои машины. Индивидуальный подход к каждому клиенту и высочайшее 
              качество работы - наши главные принципы.
            </p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-8 border border-red-900/20 text-center"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-700/20 rounded-full mb-4">
              <stat.icon className="w-8 h-8 text-red-700" />
            </div>
            <div className="text-4xl text-white mb-2">{stat.value}</div>
            <div className="text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Our Principles */}
      <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-12 border border-red-900/20">
        <h2 className="text-3xl text-center mb-12 text-white">
          Наши <span className="text-red-700">Принципы</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              title: 'Качество',
              description:
                'Мы используем только лучшие материалы и оборудование. Каждая работа выполняется с максимальным вниманием к деталям.',
            },
            {
              title: 'Индивидуальный подход',
              description:
                'Мы внимательно слушаем пожелания каждого клиента и предлагаем оптимальные решения для конкретного автомобиля.',
            },
            {
              title: 'Гарантия',
              description:
                'Мы уверены в качестве своей работы и предоставляем гарантию на все виды услуг. Ваше удовлетворение - наша цель.',
            },
          ].map((principle, index) => (
            <div key={index} className="text-center">
              <h3 className="text-xl text-white mb-4">{principle.title}</h3>
              <p className="text-gray-400 leading-relaxed">{principle.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="mt-16 bg-gradient-to-r from-red-900/30 to-red-700/30 rounded-2xl p-12 text-center border border-red-700/50">
        <h2 className="text-3xl mb-4 text-white">Хотите узнать больше?</h2>
        <p className="text-gray-300 mb-6">Свяжитесь с нами для бесплатной консультации</p>
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
