global score		= 0
global derringDo	= 10

node theBeginning {
	describe "Two roads diverge in a yellow wood. Which do you take?"
	option "the road less traveled" {
		goto lostInTheForest
	}
	option "the road with all the signs" {
		goto 
	}
}

node lostInTheForest {
	describe "You are lost in the forest, and it's getting dark."
	option "dither" {
		goto theDark
	}
	option "bravely carry on" {
		require derringDo > 5 else "You aren't brave enough to carry on."
		goto adventureTown
	}
}

node adventureTown {
	describe "Your bravery has been rewarded by arrival at that mythical funland, Adventure Town! YOU WIN!"
	end
}

node theDark {
	describe "You are eaten by a grue."
	end
}


node theMall {
	describe "You have arrived at that temple to modern American capitalism, the mall. You are sucked in by its gravitational orbit and consumed"
	end
}