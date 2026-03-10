import { useAuth } from '@/app/providers/AuthProvider';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useUIStore } from '@/infrastructure/ui/uiStore';
import { cn } from '@/lib/utils';
import { Bell, FilePlus, LogOut, Settings, User } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { isSidebarCollapsed } = useUIStore();
  const isAuthPage = ['/login', '/register'].includes(location.pathname);
  const isLegalPage = ['/cgu', '/confidentialite'].includes(location.pathname);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed', error);
    } finally {
      navigate('/login');
    }
  };

  return (
    <header
      className="sticky top-0 z-40 w-full bg-white/60 backdrop-blur-xl"
      role="banner"
      aria-label="Barre de navigation FreelanSign"
    >
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8 gap-4">
        <Link
          to={user ? '/dashboard' : '/'}
          className={cn(
            'flex items-center gap-2 transition-all duration-300',
            !isLegalPage && !isSidebarCollapsed && 'lg:opacity-0 lg:invisible',
          )}
        >
          <img src="/img/logo.png" alt="Freelansign" className="h-30" />
        </Link>
        {!isAuthPage && (
          <>
            <Button
              variant="ghost"
              size="icon"
              className="text-gray-400 hover:text-brand transition-colors"
            >
              <Bell className="h-5 w-5" />
            </Button>
            <div className="h-6 w-px bg-gray-100 mx-2" />
          </>
        )}

        <div className="flex items-center gap-4">
          {user ? (
            <>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex items-center gap-3 px-2 rounded-xl hover:bg-gray-50 transition-all border border-transparent hover:border-gray-100"
                  >
                    <div className="hidden flex-col items-end sm:flex">
                      <span className="text-xs font-bold text-gray-900 leading-none">
                        {user.profile?.first_name} {user.profile?.last_name}
                      </span>
                      <span className="text-[10px] font-medium text-gray-500 leading-none mt-1">
                        Freelance
                      </span>
                    </div>
                    <div className="h-9 w-9 rounded-lg overflow-hidden border border-gray-100 bg-gray-50 p-0.5 shadow-sm">
                      {user.profile?.avatar_url ? (
                        <img
                          src={user.profile.avatar_url}
                          alt="Avatar"
                          className="h-full w-full rounded-lg object-cover"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center rounded-lg bg-white text-gray-400">
                          <User className="h-5 w-5" />
                        </div>
                      )}
                    </div>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  className="w-64 p-2 shadow-2xl border-gray-100/50 rounded-2xl animate-in fade-in zoom-in-95 duration-100"
                >
                  <DropdownMenuLabel className="px-3 py-3">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg overflow-hidden border border-gray-100 bg-gray-50 p-0.5">
                        {user.profile?.avatar_url ? (
                          <img
                            src={user.profile.avatar_url}
                            alt="Avatar"
                            className="h-full w-full rounded-lg object-cover"
                          />
                        ) : (
                          <div className="flex h-full w-full items-center justify-center rounded-lg bg-white text-gray-400">
                            <User className="h-5 w-5" />
                          </div>
                        )}
                      </div>
                      <div className="flex flex-col min-w-0">
                        <p className="text-sm font-bold text-gray-900 truncate">
                          {user.profile?.first_name} {user.profile?.last_name}
                        </p>
                        <p className="text-[11px] font-medium text-gray-500 truncate">
                          {user.email}
                        </p>
                      </div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator className="my-2 bg-gray-50" />
                  <DropdownMenuItem
                    asChild
                    className="cursor-pointer rounded-xl focus:bg-brand/5 focus:text-brand py-2.5"
                  >
                    <Link to="/quotes/new" className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand/10 text-brand">
                        <FilePlus className="h-4 w-4" />
                      </div>
                      <span className="font-semibold">Nouveau Devis</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    asChild
                    className="cursor-pointer rounded-xl focus:bg-brand/5 focus:text-brand py-2.5"
                  >
                    <Link to="/profile" className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-100 text-gray-600">
                        <Settings className="h-4 w-4" />
                      </div>
                      <span className="font-semibold">Mon Profil</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="my-2 bg-gray-50" />
                  <DropdownMenuItem
                    onClick={handleLogout}
                    className="flex items-center gap-3 py-2.5 cursor-pointer text-destructive focus:bg-destructive/5 focus:text-destructive rounded-xl"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-destructive/10">
                      <LogOut className="h-4 w-4" />
                    </div>
                    <span className="font-semibold">Déconnexion</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <div className="flex items-center gap-3">
              {location.pathname !== '/login' && (
                <Button
                  variant="ghost"
                  size="sm"
                  asChild
                  className="text-gray-600 hover:text-brand rounded-xl"
                >
                  <Link to="/login">Connexion</Link>
                </Button>
              )}
              {location.pathname !== '/register' && (
                <Button
                  variant="default"
                  size="sm"
                  asChild
                  className="bg-brand hover:bg-brand-dark shadow-lg shadow-brand/20 rounded-xl"
                >
                  <Link to="/register">Essai gratuit</Link>
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
