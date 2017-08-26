package ZEdit;

class Splitz {

    String[] Id;
    String text;

    Splitz(String Text, String Toke) {
        this.text = Text;
        Id = Text.split(Toke);
    }

    public Splitz(String Text) {
        this(Text, " ");
    }

    void DropParen() {
        int m = Id.length - 1;
        Id[m] = Id[m].substring(0, Id[m].indexOf(')'));

        return;
    }
}
