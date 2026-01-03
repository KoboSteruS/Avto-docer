import { MapPin, Phone, Clock, Mail } from 'lucide-react';

export default function Contacts() {
  return (
    <div className="container mx-auto px-4 py-20">
      <h1 className="text-5xl text-center mb-6 text-white">
        <span className="text-red-700">Контакты</span>
      </h1>
      <p className="text-xl text-center text-gray-400 mb-16 max-w-3xl mx-auto">
        Свяжитесь с нами для консультации и записи на обслуживание
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Contact Information */}
        <div className="space-y-8">
          <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-8 border border-red-900/20">
            <h2 className="text-2xl mb-6 text-white">Контактная информация</h2>

            <div className="space-y-6">
              {/* Phone */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-red-700/20 rounded-lg flex items-center justify-center">
                  <Phone className="w-6 h-6 text-red-700" />
                </div>
                <div>
                  <div className="text-white mb-1">Телефон</div>
                  <a
                    href="tel:88142282380"
                    className="text-gray-400 hover:text-red-700 transition-colors"
                  >
                    8(8142) 28-23-80
                  </a>
                </div>
              </div>

              {/* Address */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-red-700/20 rounded-lg flex items-center justify-center">
                  <MapPin className="w-6 h-6 text-red-700" />
                </div>
                <div>
                  <div className="text-white mb-1">Адрес</div>
                  <div className="text-gray-400">
                    г. Петрозаводск, Гвардейская ул., 10
                  </div>
                </div>
              </div>

              {/* Email */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-red-700/20 rounded-lg flex items-center justify-center">
                  <Mail className="w-6 h-6 text-red-700" />
                </div>
                <div>
                  <div className="text-white mb-1">Email</div>
                  <a
                    href="mailto:info@avto-decor.ru"
                    className="text-gray-400 hover:text-red-700 transition-colors"
                  >
                    info@avto-decor.ru
                  </a>
                </div>
              </div>

              {/* Working Hours */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-red-700/20 rounded-lg flex items-center justify-center">
                  <Clock className="w-6 h-6 text-red-700" />
                </div>
                <div>
                  <div className="text-white mb-2">Режим работы</div>
                  <div className="text-gray-400 space-y-1">
                    <div>Понедельник - Пятница: 9:00 - 18:00</div>
                    <div>Суббота: 10:00 - 16:00</div>
                    <div>Воскресенье: выходной</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-8 border border-red-900/20">
            <h2 className="text-2xl mb-4 text-white">Как нас найти</h2>
            <p className="text-gray-400 leading-relaxed">
              Мы находимся в центре города. Есть удобная парковка для клиентов. 
              Рекомендуем предварительно записаться по телефону для точного планирования времени.
            </p>
          </div>
        </div>

        {/* Map */}
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg overflow-hidden border border-red-900/20 h-[600px]">
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-700 to-gray-800">
            <div className="text-center p-8">
              <MapPin className="w-16 h-16 text-red-700 mx-auto mb-4" />
              <p className="text-white text-xl mb-2">Карта</p>
              <p className="text-gray-400">
                г. Петрозаводск, Гвардейская ул., 10
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="mt-16 bg-gradient-to-r from-red-900/30 to-red-700/30 rounded-2xl p-12 text-center border border-red-700/50">
        <h2 className="text-3xl mb-4 text-white">Готовы обсудить ваш проект?</h2>
        <p className="text-gray-300 mb-6">
          Позвоните нам или приезжайте в нашу студию для бесплатной консультации
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="tel:88142282380"
            className="inline-flex items-center justify-center gap-2 bg-red-700 hover:bg-red-800 transition-colors px-8 py-4 rounded-lg text-lg"
          >
            <Phone className="w-5 h-5" />
            Позвонить
          </a>
          <a
            href="mailto:info@avto-decor.ru"
            className="inline-flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 transition-colors px-8 py-4 rounded-lg text-lg"
          >
            <Mail className="w-5 h-5" />
            Написать
          </a>
        </div>
      </div>
    </div>
  );
}
