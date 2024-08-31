#include screen.rd

//variables

int x = 420;
float y = 6.;
char hi[] = "Hello World!";
char bla = 'g';

//control flow

setBase(2000);


if (x > 100) {
    print(hi);
}
else if (x == 101){
    print("nope");
}
else {
    print("on god");
}


for (int i = 0; i < 10; i+=1) {

}



{
    int i = 0;
    while (i < 10) {
        

        i += 1;
    }
}

//pretty much c


//function

int fun(int a, int b) {
    return a+b;
}