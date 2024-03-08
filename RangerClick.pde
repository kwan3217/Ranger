PImage img;
PrintWriter ouf;
boolean mouseWasPressed=false;
int i_img=1;
int click=0;
int[] xc=new int[100];
int[] yc=new int[100];

int[] x1=new int[] {562,1061,564};
int[] y1=new int[] {477, 476,970};
final int size=50;
final int scl=10;

final String image_root="/mnt/big/workspace/Data/Ranger/";

void setup() {
    size(1010,1010);
    img=loadImage(image_root+"/7A/Ranger7A"+String.format("%03d",i_img)+".png");
    cursor(CROSS);
    ouf=createWriter(String.format("Ranger7A_2_reticle%03d.csv",i_img));
    ouf.print("tab number,xw,yw,xc0,yc0,xc1,yc1,xc2,yc2,...\n");
}

void mousePressed() {
  if(!mouseWasPressed) {
    xc[click]=mouseX/scl+x1[click]-size;
    yc[click]=mouseY/scl+y1[click]-size;
    click++;
    if(click==x1.length) {
      print(String.format("%d,%d,%d,%d",i_img,click,img.width,img.height));
      ouf.print(String.format("%d,%d,%d,%d",i_img,click,img.width,img.height));
      for(int i=0;i<click;i++) {
        print(String.format(",%d,%d",xc[i],yc[i]));
        ouf.print(String.format(",%d,%d",xc[i],yc[i]));
      }
      print("\n");
      ouf.print("\n");
      ouf.flush();
      i_img++;
      click=0;
      img=loadImage(image_root+"7A/Ranger7A"+String.format("%03d",i_img)+".png");
    }
    loop();
  }
}

void mouseReleased() {
  mouseWasPressed=false;
}
    
void draw() {
    surface.setTitle(String.format("RangerClick - TAB %03d, click %d",i_img,click));
    image(img.get(x1[click]-size,y1[click]-size,size*2+1,size*2+1),0,0,(size*2+1)*scl,(size*2+1)*scl);
    noLoop();
}
