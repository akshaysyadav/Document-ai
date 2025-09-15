import { Button } from "./ui/button";
import { Menu, X, ArrowLeft, Home, LogIn, UserPlus, User, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Avatar, AvatarFallback } from "./ui/avatar";

const Header = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  // Check login status on mount and when localStorage changes
  useEffect(() => {
    const checkLoginStatus = () => {
      const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
      setIsLoggedIn(loggedIn);
      if (loggedIn) {
        const userData = JSON.parse(localStorage.getItem('user'));
        setUser(userData);
      }
    };

    checkLoginStatus();
    window.addEventListener('storage', checkLoginStatus);
    return () => window.removeEventListener('storage', checkLoginStatus);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUser(null);
    navigate('/');
  };

  // Dark mode toggle
  const [darkMode, setDarkMode] = useState(() => {
    return document.documentElement.classList.contains('dark');
  });

  const toggleDarkMode = () => {
    setDarkMode((prev) => {
      const next = !prev;
      if (next) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return next;
    });
  };
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const getNavigationItems = () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const isKmrlStaff = user?.role === 'KMRL_STAFF';

    const publicItems = [
      { name: "Home", href: "/" },
      { name: "About", href: "/#about" },
    ];

    const normalUserItems = [
      ...publicItems,
      { name: "AI Scheduler", href: "/scheduler" },
    ];

    const staffItems = [
      ...normalUserItems,
      { name: "Documents", href: "/documents" },
      { name: "Reports", href: "/reports" },
      { name: "Dashboard", href: "/dashboard" },
    ];

    if (!isLoggedIn) return publicItems;
    return isKmrlStaff ? staffItems : normalUserItems;
  };

  const navigationItems = getNavigationItems();

  const authButtons = isLoggedIn ? (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="relative h-8 w-8 rounded-full">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-primary/10">
              {user?.username?.charAt(0)?.toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{user?.username}</p>
            <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  ) : (
    <div className="flex items-center gap-2">
      <Button 
        variant="ghost" 
        size="sm" 
        className="text-foreground hover:text-primary hover:bg-primary/10"
        asChild
      >
        <Link to="/login" className="flex items-center gap-2">
          <LogIn className="w-4 h-4" />
          <span>Login</span>
        </Link>
      </Button>
      <Button 
        variant="outline"
        size="sm"
        className="border-muted text-foreground hover:bg-muted/50 font-medium"
        asChild
      >
        <Link to="/signup" className="flex items-center gap-2">
          <UserPlus className="w-4 h-4" />
          <span>Sign Up</span>
        </Link>
      </Button>
    </div>
  );

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border shadow-sm">
      <nav className="container mx-auto px-6 py-3">
        <div className="flex items-center justify-between w-full">
          {/* Logo and Project Name shifted to left */}
          <div className="flex items-center space-x-3">
            <Link to="/" className="flex items-center space-x-3 hover:opacity-90 transition-opacity">
              <div className="bg-primary/5 p-2 rounded-xl shadow-sm">
                <img src="/train.svg" alt="KMRL Train Logo" className="w-8 h-8" />
              </div>
              <div>
                <h1 className="font-display font-bold text-xl text-foreground">KMRL AI</h1>
                <p className="text-xs text-muted-foreground">Metro Rail Solutions</p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation and Dark Mode Toggle shifted to right */}
          <div className="hidden lg:flex items-center space-x-6">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`text-foreground hover:text-primary transition-smooth font-medium px-3 py-2 rounded-lg ${
                  location.pathname === item.href 
                    ? 'text-primary bg-primary/10'
                    : 'hover:bg-muted/50'
                }`}
              >
                {item.name}
              </Link>
            ))}
            <div className="h-8 w-px bg-border mx-2" />
            {/* Dark mode toggle button - between nav and auth */}
            <Button
              variant="ghost"
              size="icon"
              aria-label="Toggle dark mode"
              onClick={toggleDarkMode}
              className="h-9 w-9 rounded-lg"
            >
              {darkMode ? (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5 text-yellow-500">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364-6.364l-1.414 1.414M6.05 17.95l-1.414 1.414M17.95 17.95l-1.414-1.414M6.05 6.05L4.636 7.464M12 8a4 4 0 100 8 4 4 0 000-8z" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </Button>
            <div className="h-8 w-px bg-border mx-2" />
            {authButtons}
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="lg:hidden mt-4 pb-4 border-t border-border">
            <div className="flex flex-col space-y-3 pt-4">
              {/* Mobile Back Button */}
              {location.pathname !== '/' && (
                <Link
                  to="/"
                  className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-smooth font-medium py-2 border-b border-border pb-3 mb-1"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <ArrowLeft size={18} />
                  <Home size={16} />
                  <span>Back to Home</span>
                </Link>
              )}
              
              {navigationItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`text-foreground hover:text-primary transition-smooth font-medium py-2 px-2 rounded-md ${
                    location.pathname === item.href ? 'text-primary bg-primary/10' : ''
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
              <div className="border-t border-border my-4 pt-4">
                {authButtons}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;