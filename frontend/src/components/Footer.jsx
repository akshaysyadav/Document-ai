import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Link } from "react-router-dom";
import { 
  Mail, 
  Phone, 
  MapPin, 
  Linkedin, 
  Twitter, 
  Globe,
  ArrowUp
} from "lucide-react";

const Footer = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const footerLinks = {
    product: [
      { name: "AI Scheduler", href: "/dashboard", isRoute: true },
      { name: "Document Automation", href: "/documents", isRoute: true },
      { name: "Reports & Analytics", href: "/reports", isRoute: true },
      { name: "Dashboard", href: "/dashboard", isRoute: true }
    ],
    company: [
      { name: "About Us", href: "#about" },
      { name: "Careers", href: "#" },
      { name: "Contact", href: "#" }
    ],
    resources: [
      { name: "API Reference", href: "#" },
      { name: "Support", href: "#" },
      { name: "Privacy Policy", href: "#" }
    ]
  };

  return (
  <footer className="bg-card text-card-foreground">
      {/* Separator line */}
      <div className="border-t border-border/30"></div>
      <div className="container mx-auto px-6 py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          {/* Company Info */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-gradient-hero flex items-center justify-center">
                <span className="text-foreground font-bold text-lg">K</span>
              </div>
              <div>
                <h3 className="font-display font-bold text-xl text-card-foreground">KMRL AI</h3>
                <p className="text-sm text-foreground">Metro Rail Solutions</p>
              </div>
            </div>
            <p className="text-white/70 mb-6 max-w-md">
              <span className="text-foreground">Revolutionizing public transportation through AI-powered scheduling and document automation. Making metro operations smarter, more efficient, and passenger-focused.</span>
            </p>
            
            {/* Contact Info */}
            <div className="text-muted-foreground hover:text-foreground transition-smooth text-sm">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <MapPin className="w-4 h-4 text-primary" />
                <span className="text-foreground">Kochi Metro Rail Limited, Kerala, India</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Mail className="w-4 h-4 text-primary" />
                <span className="text-foreground">contact@kmrlai.com</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Phone className="w-4 h-4 text-primary" />
                <span className="text-foreground">+91 484 2331 800</span>
              </div>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              {footerLinks.product.map((link, index) => (
                <li key={index}>
                  {link.isRoute ? (
                    <Link 
                      to={link.href}
                      className="text-foreground hover:text-primary transition-smooth text-sm"
                    >
                      {link.name}
                    </Link>
                  ) : (
                    <a 
                      href={link.href}
                      className="text-foreground hover:text-primary transition-smooth text-sm"
                    >
                      {link.name}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2">
              {footerLinks.company.map((link, index) => (
                <li key={index}>
                  <a 
                    href={link.href}
                    className="text-foreground hover:text-primary transition-smooth text-sm"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <Separator className="bg-white/20 mb-8" />

        {/* Bottom Footer */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col md:flex-row items-center gap-4 text-sm text-foreground">
            <span>© 2024 KMRL AI Solutions. All rights reserved.</span>
            <span className="text-muted-foreground hover:text-foreground hover:bg-muted/10 p-2">
              Powered by Advanced AI Technology
            </span>
          </div>

          {/* Social Links & Scroll to Top */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground hover:bg-muted/10 p-2">
                <Linkedin className="w-4 h-4 text-foreground" />
              </Button>
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground hover:bg-muted/10 p-2">
                <Twitter className="w-4 h-4 text-foreground" />
              </Button>
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground hover:bg-muted/10 p-2">
                <Globe className="w-4 h-4 text-foreground" />
              </Button>
            </div>
            
            <Separator orientation="vertical" className="h-6 bg-white/20" />
            
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={scrollToTop}
              className="text-foreground hover:text-primary hover:bg-muted/10 p-2"
            >
              <ArrowUp className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 pt-6 border-t border-white/20">
          <p className="text-xs text-muted-foreground text-center">
            This AI solution is designed to enhance operational efficiency while maintaining safety and compliance standards. 
            All automated decisions are subject to human oversight and approval as per regulatory requirements.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;