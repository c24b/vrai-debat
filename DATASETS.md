# DATASETS

## Vrai débat

Les méthodes d'extraction des données de la plateforme du Vrai Débat sont disponibles à cette adresse

Celle qui ont permis l'extraction des themes + des propositions (sans les arguments, les détails de votes ni les sources) sont disponible dans le script `explore.py`

### Propositions de la plateforme

* themes.json
```
{
	"_id" : ObjectId("5c85537be34ef1351e7d65e2"),
	"name" : "Démocratie, Institutions",
	"url" : "https://le-vrai-debat.fr/project/democratie-institutions-referendum-dinitiative-citoyenne/consultation/consultation/types/democratie-institutions/",
	"slug" : "democratie-institutions-referendum-dinitiative-citoyenne",
	"author" : {
		"name" : "David Prost",
		"url" : "/profile/davidprost"
	},
	"date" : "le 25 janvier 2019",
	"nb_contributions" : 20993,
	"nb_votes" : 180383,
	"nb_participants" : 12299,
	"nb_propositions" : 4232,
	"pages" : 424,
	"nb" : 1
}
```

* proposal.json


``` json
{
	"_id" : ObjectId("5c9426dce34ef1322cdb270e"),
	"titre" : "Taxer les déboutés du droit d'asile faisant appel",
	"url" : "https://le-vrai-debat.fr/projects/expression-libre/consultation/consultation-9/opinions/expression-libre-sujets-de-societe/taxer-les-deboutes-du-droit-dasile-faisant-appel",
	"date" : "31 janvier 2019 16:35",
	"auteur" : {
		"url" : "https://le-vrai-debat.fr/profile/barnabe",
		"name" : "barnabé"
	},
	"stats" : {
		"votes" : 35,
		"arguments" : 5,
		"source" : 0
	},
	"votes" : {
		"d'accord" : 14,
		"pas d'accord" : 21,
		"mitigé" : 0,
		"total" : 35
	},
	"title" : "Taxer les déboutés du droit d'asile faisant appel",
	"text" : "Réduction du délai de réponse aux demandes d'asile et réponses plus fiables avec augmentation du nombre de rejets. Pour éviter les appels systématiques des déboutés du droit d'asile imposer le versement d'une taxe significative (1000 € par exemple) aux déboutés qui font appel pour gagner du temps au lieu de quitter le pays.",
	"theme" : {
		"_id" : ObjectId("5c856d3be34ef14b3b34e911"),
		"name" : "Expression Libre & Sujets de société",
		"url" : "https://le-vrai-debat.fr/project/expression-libre/consultation/consultation-9/types/expression-libre-sujets-de-societe/",
		"slug" : "expression-libre",
		"author" : {
			"name" : "David Prost",
			"url" : "/profile/davidprost"
		},
		"date" : "le 25 janvier 2019",
		"nb_contributions" : 23950,
		"nb_votes" : 215652,
		"nb_participants" : 11311,
		"nb_propositions" : 3831,
		"pages" : 384,
		"nb" : 9
	}
}

