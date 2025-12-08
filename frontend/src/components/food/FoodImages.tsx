import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface FoodImage {
  _id: string;
  food_id: number;  // Changed to number
  image_data: string;
  mime_type: string;
  caption?: string;
  created_at: string;
}

interface FoodImagesProps {
  foodId: number;  // Changed to number
}

export const FoodImages: React.FC<FoodImagesProps> = ({ foodId }) => {
  const [images, setImages] = useState<FoodImage[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [caption, setCaption] = useState('');
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadImages();
  }, [foodId]);

  const loadImages = async () => {
    try {
      setLoading(true);
      const data = await api.mongodb.getFoodImages(foodId); // FIXED: Use mongodb.getFoodImages
      setImages(data.images || data || []);
    } catch (error) {
      console.error('Failed to load images:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const uploadImage = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('image', selectedFile);
    if (caption) formData.append('caption', caption);

    setUploading(true);
    try {
      await api.mongodb.uploadFoodImage(foodId, formData); // FIXED: Use mongodb.uploadFoodImage
      loadImages();
      setSelectedFile(null);
      setCaption('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">📸</span> Food Images
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Upload Section */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg space-y-3">
          <Input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            ref={fileInputRef}
          />
          <Input
            type="text"
            placeholder="Image caption (optional)"
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
          />
          <Button 
            onClick={uploadImage} 
            disabled={!selectedFile || uploading || loading}
            className="w-full"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : 'Upload Image'}
          </Button>
        </div>

        {/* Image Gallery */}
        {loading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        ) : images.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {images.map((image) => (
              <div key={image._id} className="border rounded-lg overflow-hidden">
                <div className="aspect-square overflow-hidden bg-gray-100">
                  <img
                    src={`data:${image.mime_type};base64,${image.image_data}`}
                    alt={image.caption || 'Food image'}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-3">
                  <p className="text-sm font-medium truncate">
                    {image.caption || 'No caption'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(image.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500 py-4">No food images uploaded yet.</p>
        )}
      </CardContent>
    </Card>
  );
};