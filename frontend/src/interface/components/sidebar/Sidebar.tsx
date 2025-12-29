import { useAuth } from '@/app/providers/AuthProvider';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/infrastructure/ui/uiStore';
import { cn } from '@/lib/utils';
import {
  ChevronRight,
  ClipboardList,
  FileText,
  LayoutDashboard,
  Palette,
  PanelLeftClose,
  PanelLeftOpen,
  PlusCircle,
  Settings,
  User,
  Users,
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const { user } = useAuth();
  const location = useLocation();
  const { isSidebarCollapsed, toggleSidebar } = useUIStore();

  const navItems = [
    { to: '/dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
    { to: '/quotes', label: 'Mes Devis', icon: ClipboardList },
    { to: '/clients', label: 'Mes Clients', icon: Users },
    { to: '/branding/themes', label: 'Branding & Thèmes', icon: Palette },
    { to: '/legal-terms', label: 'Conditions Générales', icon: FileText },
  ];

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 hidden h-screen flex-col bg-white lg:flex z-50 transition-all duration-300 shadow-[2px_0_12px_rgba(0,0,0,0.02)]',
        isSidebarCollapsed ? 'w-20' : 'w-64',
      )}
    >
      {/* Brand / Logo Area */}
      <div
        className={cn(
          'flex h-16 items-center px-4 transition-all duration-300',
          isSidebarCollapsed ? 'justify-center' : 'px-6',
        )}
      >
        <Link to="/" className="flex items-center gap-2.5 overflow-hidden">
          {!isSidebarCollapsed && (
            <span className="font-playfair text-xl font-bold text-brand whitespace-nowrap opacity-100 transition-opacity duration-300">
              FreelanSign
            </span>
          )}
        </Link>
      </div>

      {/* User Profile CTA */}
      <div className="p-4 overflow-hidden">
        <Link
          to="/profile"
          className={cn(
            'group flex items-center rounded-xl bg-gray-50/80 transition-all duration-300 hover:bg-gray-100/80 hover:shadow-sm active:scale-[0.98]',
            isSidebarCollapsed ? 'justify-center p-2' : 'gap-3 p-3',
          )}
          title={isSidebarCollapsed ? 'Mon Profil' : undefined}
        >
          <div className="relative h-10 w-10 shrink-0">
            {user?.profile?.avatar_url ? (
              <img
                src={user.profile.avatar_url}
                alt="Avatar"
                className="h-full w-full rounded-lg object-cover"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center rounded-lg bg-white text-gray-400 border border-gray-100 shadow-sm">
                <User className="h-5 w-5" />
              </div>
            )}
            <div className="absolute -bottom-1 -right-1 h-3 w-3 rounded-full bg-brand border-2 border-white" />
          </div>

          {!isSidebarCollapsed && (
            <>
              <div className="flex flex-col min-w-0 flex-1 opacity-100 transition-opacity duration-300">
                <span className="text-sm font-semibold text-gray-900 truncate">
                  {user?.profile?.first_name || 'Mon'}{' '}
                  {user?.profile?.last_name || 'Profil'}
                </span>
                <span className="text-xs text-gray-500 truncate">
                  Gérer mon compte
                </span>
              </div>
              <ChevronRight className="ml-auto h-4 w-4 text-gray-400 group-hover:text-brand group-hover:translate-x-0.5 transition-all" />
            </>
          )}
        </Link>
      </div>

      {/* Main Navigation */}
      <nav
        className="flex-1 space-y-1 px-3 py-2 overflow-y-auto overflow-x-hidden"
        aria-label="Navigation principale"
      >
        <div className="mb-6 px-1">
          <Button
            variant="default"
            size="sm"
            asChild
            className={cn(
              'w-full gap-3 bg-brand hover:bg-brand-dark shadow-lg shadow-brand/20 h-11 transition-all duration-300',
              isSidebarCollapsed
                ? 'justify-center px-0'
                : 'justify-start px-4 text-sm font-bold',
            )}
          >
            <Link to="/quotes/new" title="Nouveau Devis">
              <PlusCircle className="h-5 w-5 shrink-0" />
              {!isSidebarCollapsed && (
                <span className="truncate whitespace-nowrap">
                  Nouveau Devis
                </span>
              )}
            </Link>
          </Button>
        </div>

        {!isSidebarCollapsed && (
          <div className="px-3 mb-2 opacity-100 transition-opacity duration-300">
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
              Menu Principal
            </span>
          </div>
        )}

        {navItems.map((item) => {
          const isActive =
            location.pathname === item.to ||
            (item.to !== '/dashboard' && location.pathname.startsWith(item.to));
          return (
            <Link
              key={item.to}
              to={item.to}
              title={isSidebarCollapsed ? item.label : undefined}
              className={cn(
                'group flex items-center rounded-lg py-2.5 text-sm font-medium transition-all duration-200',
                isSidebarCollapsed ? 'justify-center px-0' : 'gap-3 px-3',
                isActive
                  ? 'bg-brand/10 text-brand font-semibold'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900',
              )}
            >
              <item.icon
                className={cn(
                  'h-5 w-5 shrink-0 transition-colors',
                  isActive
                    ? 'text-brand'
                    : 'text-gray-400 group-hover:text-gray-600',
                )}
              />
              {!isSidebarCollapsed && (
                <span className="truncate whitespace-nowrap flex-1">
                  {item.label}
                </span>
              )}
              {!isSidebarCollapsed && isActive && (
                <div className="ml-auto h-1.5 w-1.5 rounded-full bg-brand" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer Side Navigation */}
      <div className="p-3 space-y-1 bg-gray-50/30">
        <Link
          to="/profile/edit"
          title={isSidebarCollapsed ? 'Paramètres' : undefined}
          className={cn(
            'group flex items-center rounded-lg py-2.5 text-sm font-medium transition-all',
            isSidebarCollapsed ? 'justify-center px-0' : 'gap-3 px-3',
            location.pathname === '/profile/edit'
              ? 'bg-white text-gray-900 shadow-sm border border-gray-100'
              : 'text-gray-500 hover:bg-white hover:shadow-sm',
          )}
        >
          <Settings className="h-5 w-5 shrink-0 text-gray-400 group-hover:rotate-45 transition-transform" />
          {!isSidebarCollapsed && (
            <span className="truncate whitespace-nowrap">Paramètres</span>
          )}
        </Link>

        {/* Toggle Button */}
        <button
          onClick={toggleSidebar}
          className="group flex w-full items-center rounded-lg py-2.5 text-sm font-medium text-gray-400 transition-all hover:bg-white hover:shadow-sm hover:text-gray-600"
          title={isSidebarCollapsed ? 'Développer' : 'Réduire'}
        >
          <div
            className={cn(
              'flex items-center transition-all duration-300 w-full',
              isSidebarCollapsed ? 'justify-center' : 'gap-3 px-3',
            )}
          >
            {isSidebarCollapsed ? (
              <PanelLeftOpen className="h-5 w-5" />
            ) : (
              <>
                <PanelLeftClose className="h-5 w-5" />
                <span className="truncate whitespace-nowrap">Réduire</span>
              </>
            )}
          </div>
        </button>
      </div>
    </aside>
  );
}
