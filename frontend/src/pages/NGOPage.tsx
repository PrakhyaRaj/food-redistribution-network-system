import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Building2, Users, MapPin, Phone, Mail, Globe, Heart } from "lucide-react";
import { toast } from "sonner";

interface NGO {
  id: number;
  name: string;
  lat: number;
  long: number;
  phone?: string;
  email?: string;
  website?: string;
}

const ngoData: NGO[] = [
  {
    id: 1,
    name: "Vatsalya Puram",
    lat: 12.9222722,
    long: 77.5823943,
    phone: "+91 89042 78878",
    website: "http://www.vatsalyapuram.com/",
  },
  {
    id: 2,
    name: "Angel's Orphanage",
    lat: 12.9871178,
    long: 77.6002644,
    phone: "+91 98866 33094",
    email: "angelsorphanage4@gmail.com",
  },
  {
    id: 3,
    name: "MTNC Trust",
    lat: 13.0400593,
    long: 77.7398285,
    phone: "+91 63633 87310",
    website: "http://www.mtnctrust.org/",
  },
  {
    id: 4,
    name: "The Children Home",
    lat: 13.0220143,
    long: 77.6998920,
    phone: "+91 80507 32759",
    website: "http://thechildrenhome.org/",
  },
  {
    id: 5,
    name: "Sumangali Seva Ashrama",
    lat: 13.0360415,
    long: 77.5951625,
    phone: "+91 72040 01393",
    website: "https://www.sumangalisevaashrama.org/",
  },
  {
    id: 6,
    name: "Sparsha Trust",
    lat: 13.0315685,
    long: 77.5588693,
    phone: "+91 97407 55495",
    website: "http://www.sparsha.org/",
  },
  {
    id: 7,
    name: "SOS Children's Villages",
    lat: 12.8727956,
    long: 77.5961797,
    phone: "+91 80265 83615",
    website: "http://www.soschildrensvillages.in/",
  },
  {
    id: 8,
    name: "Kritagyata Foundation",
    lat: 13.1088976,
    long: 77.6074383,
    phone: "+91 99012 38222",
    website: "https://www.kritagyata.org/",
  },
  {
    id: 9,
    name: "BLESS India",
    lat: 13.01491,
    long: 77.5172789,
    phone: "+91 96636 65248",
    website: "https://www.blessindia.org.in/",
  },
  {
    id: 10,
    name: "Community Support Organization",
    lat: 12.8803928,
    long: 77.550027,
    phone: "+91 99861 62525",
  },
  {
    id: 11,
    name: "Lifting Hand Foundation",
    lat: 13.019739,
    long: 77.6288826,
    phone: "+91 97382 38031",
    website: "http://www.liftinghandfoundation.com/",
  },
  {
    id: 12,
    name: "Vara Foundations",
    lat: 12.8860217,
    long: 77.579684,
    phone: "+91 99002 27171",
    website: "http://www.varafoundations.org/",
  },
  {
    id: 13,
    name: "Janaseva Orphanage",
    lat: 12.8982167,
    long: 77.5390337,
    phone: "+91 99803 59595",
    website: "http://janasevaorphanage.org/",
  },
  {
    id: 14,
    name: "Shishu Mandir",
    lat: 13.0371158,
    long: 77.7123179,
    website: "http://www.shishumandir.org/",
  },
  {
    id: 15,
    name: "Swanthana Foundation",
    lat: 12.9024981,
    long: 77.7175804,
    phone: "+91 99869 51855",
    website: "https://swanthana.org/",
  },
];

const NGOPage = () => {
  const [selectedNGO, setSelectedNGO] = useState<NGO | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    foodName: "",
    quantity: "",
    expiryDate: "",
  });

  const handleDonateClick = (ngo: NGO) => {
    setSelectedNGO(ngo);
    setDialogOpen(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.foodName || !formData.quantity || !formData.expiryDate) {
      toast.error("Please fill in all fields");
      return;
    }

    // Show success message
    toast.success("Request has been sent", {
      description: `Your donation to ${selectedNGO?.name} has been submitted successfully.`,
    });

    // Reset form and close dialog
    setFormData({ foodName: "", quantity: "", expiryDate: "" });
    setDialogOpen(false);
    setSelectedNGO(null);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
    setSelectedNGO(null);
    setFormData({ foodName: "", quantity: "", expiryDate: "" });
  };
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Building2 className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">Match with Organizations</h1>
          <p className="text-muted-foreground">Connect with NGOs and organizations for food redistribution</p>
        </div>
      </div>

      {/* NGO Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {ngoData.map((ngo) => (
          <Card key={ngo.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-primary" />
                {ngo.name}
              </CardTitle>
              <CardDescription>NGO · Non-Profit Organization</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs">
                  {ngo.lat.toFixed(6)}, {ngo.long.toFixed(6)}
                </span>
              </div>
              
              {ngo.phone && (
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{ngo.phone}</span>
                </div>
              )}
              
              {ngo.email && (
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs">{ngo.email}</span>
                </div>
              )}
              
              {ngo.website && (
                <div className="flex items-center gap-2 text-sm">
                  <Globe className="h-4 w-4 text-muted-foreground" />
                  <a 
                    href={ngo.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-primary hover:underline truncate"
                  >
                    Visit Website
                  </a>
                </div>
              )}

              <Button 
                className="w-full mt-4" 
                onClick={() => handleDonateClick(ngo)}
              >
                <Heart className="h-4 w-4 mr-2" />
                Donate
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Donation Dialog */}
      <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Donate to {selectedNGO?.name}</DialogTitle>
            <DialogDescription>
              Fill in the details of the food you want to donate to this organization.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="foodName">Food Name</Label>
                <Input
                  id="foodName"
                  placeholder="e.g., Rice, Vegetables, Bread"
                  value={formData.foodName}
                  onChange={(e) => setFormData({ ...formData, foodName: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  placeholder="e.g., 10"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="expiryDate">Expiry Date</Label>
                <Input
                  id="expiryDate"
                  type="date"
                  value={formData.expiryDate}
                  onChange={(e) => setFormData({ ...formData, expiryDate: e.target.value })}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleDialogClose}>
                Cancel
              </Button>
              <Button type="submit">Submit Donation</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Info Section */}
      <Card className="bg-gradient-to-r from-primary/10 to-secondary/10 border-primary/20">
        <CardContent className="py-8">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <Building2 className="h-16 w-16 text-primary flex-shrink-0" />
            <div className="text-center md:text-left">
              <h3 className="text-xl font-semibold mb-2">Supporting Bangalore NGOs & Orphanages</h3>
              <p className="text-muted-foreground">
                Connect directly with {ngoData.length} verified organizations across Bangalore. 
                Your food donations help feed children and families in need. Click "Donate" on any 
                organization to submit your food donation details.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NGOPage;
