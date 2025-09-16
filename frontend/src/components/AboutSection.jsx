import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Users, 
  Award, 
  Zap
} from "lucide-react";

const AboutSection = () => {
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

        <div className="max-w-4xl mx-auto">
          {/* Achievements */}
          <div>
            <h3 className="text-2xl font-display font-bold mb-8 text-center">Recognition & Impact</h3>
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              {achievements.map((achievement, index) => (
                <div key={index} className="flex flex-col items-center text-center p-6 rounded-xl bg-muted/30 hover-lift">
                  <div className="p-3 rounded-lg bg-primary/10 mb-4">
                    <achievement.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h4 className="font-semibold mb-2">{achievement.title}</h4>
                  <p className="text-sm text-muted-foreground">{achievement.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Vision Statement */}
          <Card className="bg-primary/5 border border-primary/20">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold mb-4 text-center">Our Vision</h3>
              <p className="text-muted-foreground text-center text-lg italic">
                "To create intelligent transportation systems that seamlessly blend technology with human needs, making every journey safer, faster, and more sustainable."
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;