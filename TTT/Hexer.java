public  class  Hexer  {

static String input;
public static String printout;

public static void main(String[] args){

if(args.length>1) {
	new Hexer(args[0]+" "+args[1]);
	} else {
	new Hexer(args[0]);
	}

     }

public Hexer(String _input){
input = _input;

if(input.indexOf(' ')>0){
input = input.substring(0,input.indexOf(' '));

System.out.println(input+" equals decimal value "+ Integer.valueOf(input,16));
printout = (input+" equals decimal value "+ Integer.valueOf(input,16));
} else {
System.out.println(input+" equals hexvalue "+ Integer.toHexString( Integer.parseInt(input) ) );
printout = (input+" equals hexvalue "+ Integer.toHexString( Integer.parseInt(input) ) );
	}
}
}
