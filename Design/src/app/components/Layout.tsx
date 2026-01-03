import { Link, Outlet, useLocation } from 'react-router-dom';
import { Phone } from 'lucide-react';

export default function Layout() {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Header */}
      <header className="bg-black/50 backdrop-blur-md border-b border-red-900/20 sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between py-4">
            {/* Logo */}
            <Link to="/" className="flex flex-col items-start">
              <span className="text-3xl font-bold text-white">
                Avto<span className="text-red-700">Декор</span>
              </span>
              <span className="text-sm text-gray-400">Студия Автомобильного интерьера</span>
            </Link>

            {/* Contact */}
            <a 
              href="tel:88142282380" 
              className="flex items-center gap-2 bg-red-700 hover:bg-red-800 transition-colors px-6 py-3 rounded-lg"
            >
              <Phone className="w-5 h-5" />
              <span>8(8142) 28-23-80</span>
            </a>
          </div>

          {/* Navigation */}
          <nav className="border-t border-red-900/20">
            <ul className="flex flex-wrap gap-2 md:gap-0">
              {[
                { path: '/', label: 'ГЛАВНАЯ' },
                { path: '/services', label: 'УСЛУГИ' },
                { path: '/our-works', label: 'НАШИ РАБОТЫ' },
                { path: '/new-works', label: 'НОВЫЕ РАБОТЫ' },
                { path: '/reviews', label: 'ОТЗЫВЫ' },
                { path: '/about', label: 'О СТУДИИ' },
                { path: '/contacts', label: 'КОНТАКТЫ' },
              ].map((item) => (
                <li key={item.path} className="flex-1">
                  <Link
                    to={item.path}
                    className={`block px-4 py-4 text-center transition-colors ${
                      isActive(item.path)
                        ? 'bg-red-700 text-white'
                        : 'text-gray-300 hover:bg-red-900/30 hover:text-white'
                    }`}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-black/80 border-t border-red-900/20 mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold text-white mb-4">
                Avto<span className="text-red-700">Декор</span>
              </h3>
              <p className="text-gray-400 text-sm">
                Профессиональный тюнинг автомобильного интерьера в Петрозаводске
              </p>
            </div>
            <div>
              <h3 className="text-white mb-4">Контакты</h3>
              <p className="text-gray-400 text-sm">Телефон: 8(8142) 28-23-80</p>
              <p className="text-gray-400 text-sm">г. Петрозаводск</p>
            </div>
            <div>
              <h3 className="text-white mb-4">Режим работы</h3>
              <p className="text-gray-400 text-sm">Понедельник - Пятница: 9:00 - 18:00</p>
              <p className="text-gray-400 text-sm">Суббота: 10:00 - 16:00</p>
            </div>
          </div>
          <div className="border-t border-red-900/20 mt-8 pt-8 text-center text-gray-500 text-sm">
            © 2026 Avto-Декор. Все права защищены.
          </div>
        </div>
      </footer>
    </div>
  );
}
