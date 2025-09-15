import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Users, 
  Award, 
  Code, 
  Zap,
  Heart,
  Target
} from "lucide-react";

const AboutSection = () => {
  const teamMembers = [
    {
      name: "Shreyansh Singh",
      role: "AI Researcher",
      icon: Code,
      description: "15+ years in transportation AI"
    },
    {
      name: "Niraj Shukla",
      role: "UI/UX",
      icon: Target,
      description: "Metro operations specialist"
    },
    {
      name: "Akshay Yadav",
      role: "UI/UX Designer",
      icon: Zap,
      description: "Full-stack development expert"
    },
    {
      name: "Parag Shirke",
      role: "UX Designer",
      icon: Heart,
      description: "Human-centered design advocate"
    },
    {
      name: "Alok Singh",
      role: "PPT Expert",
      icon: Users,
      description: "Expert in PPT and presentations"
    },
    {
      name: "Pawni Gupta",
      role: "Designer",
      icon: Award,
      description: "Specialist in Designing modeling"
    }
  ];

  const achievements = [
    {
      icon: Award,
      title: "Innovation Award 2024",
      description: "Best Transportation Technology"
    },
    {
      icon: Users,
      title: "Trusted by 50+ Cities",
      description: "Metro systems worldwide"
    },
    {
      icon: Zap,
      title: "99.8% Uptime",
      description: "Reliable 24/7 operations"
    }
  ];

  return (
    <section id="about" className="py-20">
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-secondary/10 text-secondary border-secondary/20">
            Our Mission
          </Badge>
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Transforming <span className="gradient-text-hero">Public Transportation</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            We're dedicated to revolutionizing metro operations through advanced AI technology, making public transportation smarter, more efficient, and passenger-friendly.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 items-start">
          {/* About Content */}
          <div className="space-y-8">
            <div>
              <h3 className="text-2xl font-display font-bold mb-4">Our Story</h3>
              <p className="text-muted-foreground mb-4">
                Founded in partnership with Kochi Metro Rail Limited, our AI-powered solution addresses the complex challenges of modern metro operations. We combine deep domain expertise with cutting-edge artificial intelligence to create intelligent systems that learn, adapt, and optimize.
              </p>
              <p className="text-muted-foreground">
                Our platform has successfully automated scheduling processes, reduced operational costs by 35%, and improved service reliability across multiple metro networks.
              </p>
            </div>

            {/* Achievements */}
            <div>
              <h4 className="text-xl font-semibold mb-6">Recognition & Impact</h4>
              <div className="space-y-4">
                {achievements.map((achievement, index) => (
                  <div key={index} className="flex items-start gap-4 p-4 rounded-xl bg-muted/30 hover-lift">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <achievement.icon className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h5 className="font-semibold">{achievement.title}</h5>
                      <p className="text-sm text-muted-foreground">{achievement.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Team Grid */}
          <div>
            <h3 className="text-2xl font-display font-bold mb-8">Meet Our Team</h3>
            <div className="grid sm:grid-cols-2 gap-6">
              {teamMembers.map((member, index) => (
                <Card 
                  key={index} 
                  className="group relative gradient-card border-0 shadow-soft text-center transition-smooth"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Animated gradient background shift on hover */}
                  <div className="absolute inset-0 pointer-events-none transition-all duration-700 group-hover:scale-105 group-hover:blur-[2px] group-hover:brightness-110"
                    style={{
                      background: 'linear-gradient(120deg, hsl(var(--primary)/.13) 0%, hsl(var(--secondary)/.10) 100%)',
                      transition: 'background-position 0.7s cubic-bezier(0.4,0,0.2,1)',
                      backgroundSize: '200% 200%',
                      backgroundPosition: '0% 50%'
                    }}
                  />
                  <CardContent className="relative p-6 group-hover:scale-105 transition-transform duration-300">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-hero flex items-center justify-center">
                      <member.icon className="w-8 h-8 text-white" />
                    </div>
                    <h4 className="font-bold mb-1">{member.name}</h4>
                    <p className="text-primary font-medium text-sm mb-2">{member.role}</p>
                    <p className="text-xs text-muted-foreground">{member.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Vision Statement */}
            <Card className="mt-8 gradient-card border-0 shadow-medium">
              <CardContent className="p-8">
                <h4 className="text-xl font-bold mb-4 text-center">Our Vision</h4>
                <p className="text-muted-foreground text-center italic">
                  "To create intelligent transportation systems that seamlessly blend technology with human needs, making every journey safer, faster, and more sustainable."
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;