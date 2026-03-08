

function CategoryAccordion({index,title,content}) {

    return (
        <div className="accordion" id={`accordion-${index}`}>
            <div className="accordion-item">
                <h2 className="accordion-header">
                    <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target={`#collapse-${index}`} aria-expanded="false" aria-controls={`collapse-${index}`}>
                        <label className="category-label"> {title} </label>
                    </button>
                </h2>
                <div id={`collapse-${index}`} className="accordion-collapse collapse" data-bs-parent={`#accordion-${index}`}>
                    <div className="accordion-body">
                        {content.length === 0 && <p>No quiz for this category yet</p>}
                        {content.map((theme, i) => 
                                        <label className="theme-label" key={i}> <a href={`/theme/${theme.name}`}>{theme.name}</a> ({theme.quizCount}) &nbsp; </label>
                                        )}
                    </div>
                </div>
            </div>
        </div>
    );

}

export default CategoryAccordion