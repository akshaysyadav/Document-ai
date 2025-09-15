import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Scan, 
  Search, 
  Tags, 
  FileText, 
  ArrowRight,
  Database,
  Zap,
  CheckCircle
} from "lucide-react";
import documentAutomation from "@/assets/document-automation.jpg";

const DocumentAutomationSection = () => {
  const features = [
    {
      icon: Scan,
      title: "Auto-Scan Documents",
      description: "Automatically digitize invoices, reports, and job cards with 99.8% accuracy"
    },
    {
      icon: Database,
      title: "Extract Key Data",
      description: "AI extracts critical information and structures it for easy access"
    },
    {
      icon: Search,
      title: "Instant Search",
      description: "Find any document or data point in milliseconds across thousands of files"
    },
    {
      icon: Tags,
      title: "Smart Tagging",
      description: "Intelligent categorization and tagging for seamless organization"
    }
  ];

  const documentStats = [
    { label: "Documents Processed", value: "1.2M+", icon: FileText },
    { label: "Processing Speed", value: "< 2 sec", icon: Zap },
    { label: "Accuracy Rate", value: "99.8%", icon: CheckCircle }
  ];

  return (
    <section id="documents" className="py-20">
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-secondary/10 text-secondary border-secondary/20">
            Document Intelligence
          </Badge>
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            AI-Powered <span className="gradient-text-hero">Document Automation</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Transform thousands of physical documents into an intelligent, searchable digital database with advanced AI scanning and organization.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Visual */}
          <div className="relative">
            <div className="relative overflow-hidden rounded-2xl shadow-strong">
              <img 
                src={documentAutomation}
                alt="Document automation transformation"
                className="w-full h-auto"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/20 via-transparent to-transparent" />
            </div>
            
            {/* Floating Stats */}
            <div className="absolute -bottom-6 -right-6 bg-card shadow-strong rounded-2xl p-4 border animate-float">
              <div className="text-2xl font-bold gradient-text-hero">1.2M+</div>
              <div className="text-sm text-muted-foreground">Documents Processed</div>
            </div>
          </div>

          {/* Content */}
          <div>
            <h3 className="text-2xl font-display font-bold mb-8">Intelligent Document Processing</h3>
            
            {/* Features Grid */}
            <div className="grid gap-6 mb-8">
              {features.map((feature, index) => (
                <Card 
                  key={index} 
                  className="hover-lift gradient-card border-0 shadow-soft"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <CardContent className="p-6 flex items-start gap-4">
                    <div className="p-2 rounded-lg bg-secondary/10">
                      <feature.icon className="w-6 h-6 text-secondary" />
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">{feature.title}</h4>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              {documentStats.map((stat, index) => (
                <div key={index} className="text-center">
                  <stat.icon className="w-6 h-6 text-secondary mx-auto mb-2" />
                  <div className="text-2xl font-bold gradient-text-hero">
                    {stat.value}
                  </div>
                  <div className="text-xs text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div>

            {/* CTA */}
            <Button 
              size="lg" 
              className="w-full gradient-hero text-white border-0 hover:opacity-90 hover-lift"
            >
              Explore Documents
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DocumentAutomationSection;